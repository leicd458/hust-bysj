"""
推理脚本 - 使用训练好的模型进行预测
适合深度学习零基础的同学：这个脚本就像"考试"，用训练好的模型对新图片进行诊断
"""
import os
import sys
import torch
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import seaborn
import seaborn as sns
sns.set_theme()
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['font.sans-serif'] = ['SimHei']
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from config import config
from models.resnet_classifier import ResNetClassifier
from models.unet_segmentor import UNet
from utils.grad_cam import GradCAM
from dataset import get_transforms

class BreastCancerDiagnosisSystem:
    """
    乳腺癌诊断系统
    
    功能：
    1. 分类：判断图片是正常、良性还是恶性
    2. 分割：标记出肿瘤区域
    3. 可解释性：显示模型关注的区域
    """
    
    def __init__(self, classifier_path, segmentor_path=None):
        """
        初始化诊断系统
        
        参数：
            classifier_path: 分类模型路径
            segmentor_path: 分割模型路径（可选）
        """
        self.device = config.device
        self.class_names = config.class_names
        
        # 加载分类模型
        print("加载分类模型...")
        self.classifier = ResNetClassifier(
            num_classes=config.num_classes,
            pretrained=False
        ).to(self.device)
        
        checkpoint = torch.load(classifier_path, map_location=self.device)
        self.classifier.load_state_dict(checkpoint['model_state_dict'])
        self.classifier.eval()
        print("✓ 分类模型加载完成")
        
        # 加载分割模型（如果提供）
        self.segmentor = None
        if segmentor_path and os.path.exists(segmentor_path):
            print("加载分割模型...")
            self.segmentor = UNet(
                in_channels=3,
                out_channels=1,
                features=config.unet_features
            ).to(self.device)
            
            checkpoint = torch.load(segmentor_path, map_location=self.device)
            self.segmentor.load_state_dict(checkpoint['model_state_dict'])
            self.segmentor.eval()
            print("✓ 分割模型加载完成")
        
        # 初始化Grad-CAM
        self.grad_cam = GradCAM(
            self.classifier,
            target_layer=self.classifier.resnet.layer4
        )
        
        # 数据变换
        self.transform = get_transforms(
            image_size=config.image_size,
            augmentation=False
        )
    
    def preprocess_image(self, image_path):
        """
        预处理图片
        
        参数：
            image_path: 图片路径
        
        返回：
            image_tensor: 预处理后的图片张量
            original_image: 原始图片
        """
        # 读取图片
        original_image = Image.open(image_path).convert('RGB')
        
        # 应用变换
        image_tensor = self.transform(original_image)
        image_tensor = image_tensor.unsqueeze(0)  # 添加batch维度
        
        return image_tensor, original_image
    
    def classify(self, image_tensor):
        """
        分类预测
        
        参数：
            image_tensor: 图片张量
        
        返回：
            predicted_class: 预测类别
            confidence: 置信度
            probabilities: 各类别概率
        """
        with torch.no_grad():
            image_tensor = image_tensor.to(self.device)
            outputs = self.classifier(image_tensor)
            probabilities = torch.softmax(outputs, dim=1)[0]
            
            predicted_idx = probabilities.argmax().item()
            predicted_class = self.class_names[predicted_idx]
            confidence = probabilities[predicted_idx].item()
        
        return predicted_class, confidence, probabilities.cpu().numpy()
    
    def segment(self, image_tensor):
        """
        分割预测
        
        参数：
            image_tensor: 图片张量
        
        返回：
            mask: 分割掩码
        """
        if self.segmentor is None:
            return None
        
        with torch.no_grad():
            image_tensor = image_tensor.to(self.device)
            output = self.segmentor(image_tensor)
            mask = torch.sigmoid(output) > 0.5
            mask = mask[0, 0].cpu().numpy()
        
        return mask
    
    def explain(self, image_tensor, target_class=None):
        """
        生成可解释性热力图
        
        参数：
            image_tensor: 图片张量
            target_class: 目标类别（如果为None，使用预测类别）
        
        返回：
            cam: 热力图
            visualization: 可视化结果
        """
        cam = self.grad_cam.generate_cam(image_tensor, target_class)
        visualization = self.grad_cam.visualize(image_tensor, cam)
        
        return cam, visualization
    
    def diagnose(self, image_path, save_dir=None):
        """
        完整诊断流程
        
        参数：
            image_path: 图片路径
            save_dir: 结果保存目录
        
        返回：
            results: 诊断结果字典
        """
        print(f"
正在诊断: {image_path}")
        print("=" * 60)
        
        # 1. 预处理
        image_tensor, original_image = self.preprocess_image(image_path)
        
        # 2. 分类
        predicted_class, confidence, probabilities = self.classify(image_tensor)
        
        print(f"分类结果: {predicted_class}")
        print(f"置信度: {confidence:.2%}")
        print(f"各类别概率:")
        for i, class_name in enumerate(self.class_names):
            print(f"  {class_name}: {probabilities[i]:.2%}")
        
        # 3. 分割
        mask = None
        if self.segmentor:
            mask = self.segment(image_tensor)
            print(f"分割完成")
        
        # 4. 可解释性
        cam, grad_cam_vis = self.explain(image_tensor)
        print(f"Grad-CAM生成完成")
        
        # 5. 可视化结果
        if save_dir:
            os.makedirs(save_dir, exist_ok=True)
            self._visualize_results(
                original_image,
                predicted_class,
                confidence,
                probabilities,
                mask,
                grad_cam_vis,
                save_dir
            )
        
        results = {
            'predicted_class': predicted_class,
            'confidence': confidence,
            'probabilities': {
                class_name: float(prob)
                for class_name, prob in zip(self.class_names, probabilities)
            },
            'has_segmentation': mask is not None
        }
        
        return results
    
    def _visualize_results(self, original_image, predicted_class, confidence,
                          probabilities, mask, grad_cam_vis, save_dir):
        """可视化诊断结果"""
        fig = plt.figure(figsize=(20, 5))
        
        # 1. 原始图片
        ax1 = plt.subplot(1, 4, 1)
        ax1.imshow(original_image)
        ax1.set_title('原始图片', fontsize=14)
        ax1.axis('off')
        
        # 2. 分类结果
        ax2 = plt.subplot(1, 4, 2)
        colors = ['green' if i == self.class_names.index(predicted_class) else 'gray'
                 for i in range(len(self.class_names))]
        ax2.barh(self.class_names, probabilities, color=colors)
        ax2.set_xlabel('概率', fontsize=12)
        ax2.set_title(f'分类结果: {predicted_class}
置信度: {confidence:.2%}', fontsize=14)
        ax2.set_xlim([0, 1])
        
        # 3. Grad-CAM
        ax3 = plt.subplot(1, 4, 3)
        ax3.imshow(grad_cam_vis)
        ax3.set_title('Grad-CAM可解释性', fontsize=14)
        ax3.axis('off')
        
        # 4. 分割结果
        ax4 = plt.subplot(1, 4, 4)
        if mask is not None:
            ax4.imshow(original_image)
            ax4.imshow(mask, alpha=0.5, cmap='Reds')
            ax4.set_title('肿瘤区域分割', fontsize=14)
        else:
            ax4.text(0.5, 0.5, '未加载分割模型', 
                    ha='center', va='center', fontsize=14)
            ax4.set_title('分割结果', fontsize=14)
        ax4.axis('off')
        
        plt.tight_layout()
        
        # 保存结果
        result_path = os.path.join(save_dir, 'diagnosis_result.png')
        plt.savefig(result_path, dpi=300, bbox_inches='tight')
        print(f"
诊断结果已保存到: {result_path}")
        plt.close()


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='乳腺癌超声图像诊断系统')
    parser.add_argument('--image', type=str, required=True, help='输入图片路径')
    parser.add_argument('--classifier', type=str, 
                       default='./checkpoints/best_classifier.pth',
                       help='分类模型路径')
    parser.add_argument('--segmentor', type=str,
                       default='./checkpoints/best_segmentor.pth',
                       help='分割模型路径')
    parser.add_argument('--output', type=str, default='./results/inference',
                       help='结果保存目录')
    
    args = parser.parse_args()
    
    # 创建诊断系统
    system = BreastCancerDiagnosisSystem(
        classifier_path=args.classifier,
        segmentor_path=args.segmentor
    )
    
    # 执行诊断
    results = system.diagnose(args.image, save_dir=args.output)
    
    print("
" + "=" * 60)
    print("诊断完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
