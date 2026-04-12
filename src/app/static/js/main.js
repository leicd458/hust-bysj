/**
 * 前端交互逻辑
 */

let selectedFile = null;
let originalImageBase64 = null; // 保存原图 base64

/**
 * 初始化应用
 */
function initApp() {
    const uploadArea = document.getElementById('uploadArea');
    const imageInput = document.getElementById('imageInput');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const changeImageBtn = document.getElementById('changeImage');
    
    // 点击上传区域
    uploadArea.addEventListener('click', () => {
        imageInput.click();
    });
    
    // 文件选择
    imageInput.addEventListener('change', handleFileSelect);
    
    // 拖拽上传
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('drag-over');
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('drag-over');
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('drag-over');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });
    
    // 分析按钮
    analyzeBtn.addEventListener('click', analyzeImage);
    
    // 更换图像按钮
    changeImageBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        imageInput.click();
    });
}

/**
 * 处理文件选择
 */
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        handleFile(file);
    }
}

/**
 * 处理文件
 */
function handleFile(file) {
    console.log('处理文件:', file.name, '类型:', file.type, '大小:', file.size);
    
    // 验证文件类型 - 支持更多 MIME 类型和文件扩展名检查
    const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/bmp', 'image/webp'];
    const allowedExtensions = ['.png', '.jpg', '.jpeg', '.bmp', '.webp'];
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    
    const isValidType = allowedTypes.includes(file.type) || allowedExtensions.includes(fileExtension);
    
    if (!isValidType) {
        alert('不支持的文件格式！请上传 PNG, JPG, JPEG 或 BMP 格式的图像。\n当前文件类型: ' + file.type);
        return;
    }
    
    // 验证文件大小 (16MB)
    if (file.size > 16 * 1024 * 1024) {
        alert('文件过大！请上传小于 16MB 的图像。');
        return;
    }
    
    selectedFile = file;

    // 显示预览
    const reader = new FileReader();
    reader.onload = (e) => {
        console.log('FileReader 成功读取文件');

        // 保存原图 base64 用于后续对比显示
        originalImageBase64 = e.target.result;

        const previewImage = document.getElementById('previewImage');
        previewImage.src = e.target.result;
        previewImage.alt = file.name;

        document.getElementById('uploadPlaceholder').style.display = 'none';
        document.getElementById('previewContainer').style.display = 'flex';
        document.getElementById('analyzeBtn').disabled = false;
    };
    reader.onerror = (e) => {
        console.error('FileReader 错误:', e);
        alert('读取文件失败，请重试！');
    };
    reader.readAsDataURL(file);
    
    // 隐藏之前的结果
    document.getElementById('resultSection').style.display = 'none';
}

/**
 * 分析图像
 */
async function analyzeImage() {
    if (!selectedFile) {
        alert('请先选择图像！');
        return;
    }
    
    const analyzeBtn = document.getElementById('analyzeBtn');
    const btnText = analyzeBtn.querySelector('.btn-text');
    const btnLoading = analyzeBtn.querySelector('.btn-loading');
    
    // 显示加载状态
    btnText.style.display = 'none';
    btnLoading.style.display = 'inline';
    analyzeBtn.disabled = true;
    
    // 准备表单数据
    const formData = new FormData();
    formData.append('file', selectedFile);
    
    try {
        const response = await fetch('/predict', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayResult(data.result);
        } else {
            alert('分析失败: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('网络错误，请重试！');
    } finally {
        // 恢复按钮状态
        btnText.style.display = 'inline';
        btnLoading.style.display = 'none';
        analyzeBtn.disabled = false;
    }
}

/**
 * 显示结果
 */
function displayResult(result) {
    const resultSection = document.getElementById('resultSection');
    resultSection.style.display = 'block';
    
    // 滚动到结果区域
    resultSection.scrollIntoView({ behavior: 'smooth' });
    
    // 显示诊断结果
    document.getElementById('diagnosisClass').textContent = result.predicted_class_cn;
    document.getElementById('confidenceValue').textContent = (result.confidence * 100).toFixed(2) + '%';
    
    // 显示概率条
    const probs = result.probabilities;
    
    // Benign
    const probBenign = (probs.benign * 100).toFixed(2);
    document.getElementById('probBenign').style.width = probBenign + '%';
    document.getElementById('probBenignValue').textContent = probBenign + '%';
    
    // Malignant
    const probMalignant = (probs.malignant * 100).toFixed(2);
    document.getElementById('probMalignant').style.width = probMalignant + '%';
    document.getElementById('probMalignantValue').textContent = probMalignant + '%';
    
    // Normal
    const probNormal = (probs.normal * 100).toFixed(2);
    document.getElementById('probNormal').style.width = probNormal + '%';
    document.getElementById('probNormalValue').textContent = probNormal + '%';
    
    // 显示原始图像和Grad-CAM图像对比
    const originalImage = document.getElementById('originalImage');
    const gradcamImage = document.getElementById('gradcamImage');

    // 显示原图
    originalImage.src = originalImageBase64;
    originalImage.style.display = 'block';

    // 显示热力图
    gradcamImage.src = result.gradcam;
    gradcamImage.style.display = 'block';
}
