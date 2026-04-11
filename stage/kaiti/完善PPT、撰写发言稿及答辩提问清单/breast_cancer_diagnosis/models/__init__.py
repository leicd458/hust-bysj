"""
模型模块初始化文件
"""
from .resnet_classifier import ResNetClassifier
from .unet_segmentor import UNet

__all__ = ['ResNetClassifier', 'UNet']
