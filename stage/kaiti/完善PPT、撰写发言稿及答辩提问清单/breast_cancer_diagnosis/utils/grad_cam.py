"""
Grad-CAM可解释性模块
适合深度学习零基础的同学：Grad-CAM就像给AI的"思考过程"加上高亮笔，让我们看到它关注图片的哪些部分

什么是Grad-CAM？
- Gradient-weighted Class Activation Mapping（梯度加权类激活映射）
- 2017年提出，用于可视化CNN的决策依据
- 通过梯度信息，生成热力图，显示模型关注的区域
- 红色区域=模型认为最重要的部分，蓝色区域=不重要的部分
"""
import torch
import torch.nn.functional as F
import numpy as np
import cv2
from PIL import Image

class GradCAM:
    """
    Grad-CAM实现类
    
    工作原理（通俗解释）：
    1. 把图片输入模型，得到预测结果
    2. 计算预测结果对目标层特征图的梯度（就像求"影响力"）
    3. 用梯度对特征图加权求和，得到热力图
    4. 把热力图叠加到原图上，就能看到模型关注哪里
    
    举例说明：
    - 输入：一张乳腺超声图像
    - 输出：带热力图的图像，红色区域表示模型认为是肿瘤的地方
    """
    
    def __init__(self, model, target_layer):
        """
        初始化Grad-CAM
        
        参数说明：
            model: 训练好的模型（如ResNet18）
            target_layer: 目标层（通常是最后一个卷积层）
                         对于ResNet18，是 model.resnet.layer4
        """
        self.model = model
        self.target_layer = target_layer
        
        # 用于存储前向传播和反向传播的中间结果
        self.gradients = None  # 梯度
        self.activations = None  # 激活值（特征图）
        
        # 注册钩子函数（hook）
        # 什么是hook？就像"监听器"，在特定时刻自动执行
        self._register_hooks()
    
    def _register_hooks(self):
        """
        注册钩子函数
        
        前向钩子：在前向传播时保存特征图
        反向钩子：在反向传播时保存梯度
        """
        def forward_hook(module, input, output):
            """前向传播钩子：保存特征图"""
            self.activations = output.detach()
        
        def backward_hook(module, grad_input, grad_output):
            """反向传播钩子：保存梯度"""
            self.gradients = grad_output[0].detach()
        
        # 注册钩子到目标层
        self.target_layer.register_forward_hook(forward_hook)
        self.target_layer.register_full_backward_hook(backward_hook)
    
    def generate_cam(self, input_image, target_class=None):
        """
        生成类激活映射（CAM）
        
        参数说明：
            input_image: 输入图片，形状 [1, 3, 224, 224]
            target_class: 目标类别索引（如果为None，使用预测类别）
        
        返回：
            cam: 热力图，形状 [224, 224]，值范围 [0, 1]
        """
        # 1. 前向传播，获取预测结果
        self.model.eval()  # 设置为评估模式
        output = self.model(input_image)
        
        # 2. 确定目标类别
        if target_class is None:
            target_class = output.argmax(dim=1).item()
        
        # 3. 反向传播，计算梯度
        self.model.zero_grad()  # 清空之前的梯度
        
        # 创建one-hot编码（只有目标类别为1，其他为0）
        one_hot = torch.zeros_like(output)
        one_hot[0][target_class] = 1
        
        # 反向传播
        output.backward(gradient=one_hot, retain_graph=True)
        
        # 4. 计算权重（对梯度进行全局平均池化）
        # 梯度形状：[1, 512, 7, 7]（以ResNet18为例）
        # 权重形状：[512]
        weights = self.gradients.mean(dim=(2, 3), keepdim=True)
        
        # 5. 加权求和，生成CAM
        # activations形状：[1, 512, 7, 7]
        # weights形状：[1, 512, 1, 1]
        # cam形状：[1, 1, 7, 7]
        cam = (weights * self.activations).sum(dim=1, keepdim=True)
        
        # 6. ReLU激活（只保留正值）
        cam = F.relu(cam)
        
        # 7. 归一化到[0, 1]
        cam = cam.squeeze().cpu().numpy()
        cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-8)
        
        # 8. 调整大小到输入图片尺寸
        cam = cv2.resize(cam, (input_image.shape[3], input_image.shape[2]))
        
        return cam
    
    def visualize(self, input_image, cam, alpha=0.5):
        """
        可视化Grad-CAM结果
        
        参数说明：
            input_image: 原始输入图片，形状 [1, 3, 224, 224]
            cam: 热力图，形状 [224, 224]
            alpha: 热力图透明度（0-1之间）
        
        返回：
            visualization: 叠加后的图片，PIL Image格式
        """
        # 1. 将输入图片转换为numpy数组
        # 反归一化（恢复到[0, 255]）
        mean = np.array([0.485, 0.456, 0.406])
        std = np.array([0.229, 0.224, 0.225])
        
        img = input_image.squeeze().cpu().numpy().transpose(1, 2, 0)
        img = std * img + mean
        img = np.clip(img, 0, 1)
        img = (img * 255).astype(np.uint8)
        
        # 2. 将热力图转换为彩色（使用JET色彩映射）
        # JET色彩：蓝色(冷) -> 绿色 -> 黄色 -> 红色(热)
        heatmap = cv2.applyColorMap(np.uint8(255 * cam), cv2.COLORMAP_JET)
        heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
        
        # 3. 叠加热力图和原图
        visualization = heatmap * alpha + img * (1 - alpha)
        visualization = np.clip(visualization, 0, 255).astype(np.uint8)
        
        # 4. 转换为PIL Image
        visualization = Image.fromarray(visualization)
        
        return visualization


# 测试代码
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Grad-CAM模块测试")
    print("=" * 60)
    
    # 创建一个简单的测试模型
    from torchvision.models import resnet18
    model = resnet18(pretrained=False)
    model.eval()
    
    # 创建Grad-CAM对象
    grad_cam = GradCAM(model, target_layer=model.layer4)
    
    # 创建随机输入
    dummy_input = torch.randn(1, 3, 224, 224)
    
    # 生成CAM
    cam = grad_cam.generate_cam(dummy_input)
    print(f"CAM形状: {cam.shape}")
    print(f"CAM值范围: [{cam.min():.4f}, {cam.max():.4f}]")
    
    # 可视化
    visualization = grad_cam.visualize(dummy_input, cam)
    print(f"可视化结果类型: {type(visualization)}")
    print(f"可视化结果尺寸: {visualization.size}")
    
    print("\nGrad-CAM模块测试完成！")
