/**
 * 前端交互逻辑
 * 支持: 单图分析 / TTA增强 / 批量分析 / 历史记录
 */

let selectedFile = null;
let selectedFiles = [];       // 批量模式
let originalImageBase64 = null;
let useTTA = true;             // 默认开启 TTA
let batchMode = false;         // 批量模式开关

/**
 * 初始化应用
 */
function initApp() {
    const uploadArea = document.getElementById('uploadArea');
    const imageInput = document.getElementById('imageInput');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const changeImageBtn = document.getElementById('changeImage');
    const ttaToggle = document.getElementById('ttaToggle');
    const batchToggle = document.getElementById('batchToggle');

    // 点击上传区域
    if (uploadArea) {
        uploadArea.addEventListener('click', () => imageInput.click());
    }

    // 文件选择
    imageInput.addEventListener('change', handleFileSelect);

    // 拖拽上传
    if (uploadArea) {
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
                if (batchMode) handleBatchFiles(files);
                else handleFile(files[0]);
            }
        });
    }

    // 分析按钮
    if (analyzeBtn) analyzeBtn.addEventListener('click', analyzeImage);

    // 更换图像按钮
    if (changeImageBtn) {
        changeImageBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            imageInput.click();
        });
    }

    // TTA 开关
    if (ttaToggle) {
        ttaToggle.addEventListener('change', () => {
            useTTA = ttaToggle.checked;
            updateModeLabel();
        });
        // 初始化标签
        updateModeLabel();
    }

    // 批量模式开关
    if (batchToggle) {
        batchToggle.addEventListener('change', () => {
            batchMode = batchToggle.checked;
            toggleBatchUI(batchMode);
            resetUpload();
        });
    }
}

function updateModeLabel() {
    const label = document.getElementById('ttaLabel');
    if (label) {
        label.textContent = useTTA ? 'TTA 增强推理（推荐）' : '标准推理';
    }
}

/**
 * 切换批量 UI 显示
 */
function toggleBatchUI(isBatch) {
    const batchHint = document.getElementById('batchHint');
    const singleHint = document.getElementById('singleHint');
    if (batchHint) batchHint.style.display = isBatch ? 'block' : 'none';
    if (singleHint) singleHint.style.display = isBatch ? 'none' : 'block';

    // 更新 input multiple 属性
    const imageInput = document.getElementById('imageInput');
    if (imageInput) imageInput.multiple = isBatch;

    // 更新按钮文字
    const btnText = document.querySelector('#analyzeBtn .btn-text');
    if (btnText) btnText.textContent = isBatch ? '📊 批量分析' : '🔍 开始分析';
}

/**
 * 重置上传区域
 */
function resetUpload() {
    selectedFile = null;
    selectedFiles = [];
    originalImageBase64 = null;
    const previewContainer = document.getElementById('previewContainer');
    const uploadPlaceholder = document.getElementById('uploadPlaceholder');
    const batchPreviewList = document.getElementById('batchPreviewList');
    const resultSection = document.getElementById('resultSection');

    if (previewContainer) previewContainer.style.display = 'none';
    if (uploadPlaceholder) uploadPlaceholder.style.display = 'flex';
    if (batchPreviewList) batchPreviewList.innerHTML = '';
    if (resultSection) resultSection.style.display = 'none';

    const analyzeBtn = document.getElementById('analyzeBtn');
    if (analyzeBtn) analyzeBtn.disabled = true;

    const imageInput = document.getElementById('imageInput');
    if (imageInput) imageInput.value = '';
}

// ==================== 单图模式 ====================

function handleFileSelect(e) {
    const files = Array.from(e.target.files);
    if (!files.length) return;

    if (batchMode) {
        handleBatchFiles(files);
    } else {
        handleFile(files[0]);
    }
}

function handleFile(file) {
    if (!validateFile(file)) return;

    selectedFile = file;
    const reader = new FileReader();
    reader.onload = (e) => {
        originalImageBase64 = e.target.result;

        const previewImage = document.getElementById('previewImage');
        if (previewImage) {
            previewImage.src = e.target.result;
            previewImage.alt = file.name;
        }
        document.getElementById('uploadPlaceholder').style.display = 'none';
        document.getElementById('previewContainer').style.display = 'flex';
        document.getElementById('analyzeBtn').disabled = false;
    };
    reader.readAsDataURL(file);

    document.getElementById('resultSection').style.display = 'none';
}

// ==================== 批量模式 ====================

function handleBatchFiles(fileList) {
    const files = Array.from(fileList).filter(f => validateFile(f, true));
    if (!files.length) return;

    selectedFiles = files;
    const listEl = document.getElementById('batchPreviewList');
    listEl.innerHTML = '';

    files.forEach((f, i) => {
        const item = document.createElement('div');
        item.className = 'batch-item';
        item.innerHTML = `
            <span class="batch-item-name">${f.name}</span>
            <span class="batch-item-size">${formatSize(f.size)}</span>
            <button class="batch-item-remove" data-index="${i}">&times;</button>
        `;
        item.querySelector('.batch-item-remove').onclick = () => removeBatchItem(i);
        listEl.appendChild(item);
    });

    document.getElementById('uploadPlaceholder').style.display = 'none';
    document.getElementById('batchPreviewContainer').style.display = 'block';
    document.getElementById('analyzeBtn').disabled = false;
}

function removeBatchItem(index) {
    selectedFiles.splice(index, 1);
    if (selectedFiles.length === 0) {
        resetUpload();
    } else {
        handleBatchFiles(selectedFiles);
    }
}

// ==================== 验证 & 分析 ====================

function validateFile(file, silent=false) {
    const allowedTypes = ['image/png','image/jpeg','image/jpg','image/bmp'];
    const ext = '.' + file.name.split('.').pop().toLowerCase();
    const allowedExts = ['.png','.jpg','.jpeg','.bmp'];

    if (!allowedTypes.includes(file.type) && !allowedExts.includes(ext)) {
        if (!silent) alert('不支持的格式！请使用 PNG/JPG/BMP 图像。');
        return false;
    }
    if (file.size > 16 * 1024 * 1024) {
        if (!silent) alert('文件过大！请小于 16MB。');
        return false;
    }
    return true;
}

async function analyzeImage() {
    let endpoint, formData;

    if (batchMode && selectedFiles.length > 1) {
        // 批量模式
        endpoint = '/predict_batch';
        formData = new FormData();
        selectedFiles.forEach(f => formData.append('files', f));
    } else {
        // 单图模式
        endpoint = useTTA ? '/predict_tta' : '/predict';
        formData = new FormData();
        formData.append('file', selectedFile || selectedFiles[0]);
    }

    const analyzeBtn = document.getElementById('analyzeBtn');
    const btnText = analyzeBtn.querySelector('.btn-text');
    const btnLoading = analyzeBtn.querySelector('.btn-loading');

    btnText.style.display = 'none';
    btnLoading.style.display = 'inline';
    analyzeBtn.disabled = true;

    try {
        const t0 = performance.now();
        const response = await fetch(endpoint, { method: 'POST', body: formData });
        const elapsed = (performance.now() - t0).toFixed(0);
        const data = await response.json();

        if (data.success) {
            if (batchMode && selectedFiles.length > 1) {
                displayBatchResult(data, elapsed);
            } else {
                displayResult(data.result, elapsed);
            }
        } else {
            alert('分析失败: ' + data.error);
        }
    } catch (error) {
        console.error(error);
        alert('网络错误，请重试！');
    } finally {
        btnText.style.display = 'inline';
        btnLoading.style.display = 'none';
        analyzeBtn.disabled = false;
    }
}

// ==================== 结果展示 ====================

function displayResult(result, timeMs=0) {
    const section = document.getElementById('resultSection');
    section.style.display = 'block';
    section.scrollIntoView({ behavior: 'smooth' });

    // 诊断结果
    const cls = document.getElementById('diagnosisClass');
    cls.textContent = result.predicted_class_cn || '-';
    cls.className = 'diagnosis-class ' + (result.predicted_class || '');

    document.getElementById('confidenceValue').textContent =
        (result.confidence * 100).toFixed(2) + '%';

    // 概率条
    ['benign','malignant','normal'].forEach(name => {
        const pct = (result.probabilities[name] * 100).toFixed(2);
        document.getElementById(`prob${name.charAt(0).toUpperCase()+name.slice(1)}`).style.width = pct + '%';
        document.getElementById(`prob${name.charAt(0).toUpperCase()+name.slice(1)}Value`).textContent = pct + '%';
    });

    // Grad-CAM
    const origImg = document.getElementById('originalImage');
    const camImg = document.getElementById('gradcamImage');
    origImg.src = originalImageBase64;
    origImg.style.display = 'block';
    camImg.src = result.gradcam || '';
    camImg.style.display = result.gradcam ? 'block' : 'none';

    // 推理信息
    const infoEl = document.getElementById('inferenceInfo');
    if (infoEl) {
        infoEl.textContent = `推理耗时: ${timeMs}ms | 模式: ${useTTA ? 'TTA ('+(result.tta_augments||7)+'增强)' : '标准'}`;
    }
}

function displayBatchResult(data, timeMs) {
    const section = document.getElementById('resultSection');
    section.style.display = 'block';
    section.scrollIntoView({ behavior: 'smooth' });

    // 批量摘要
    const summaryDiv = document.getElementById('batchSummary');
    if (summaryDiv) {
        const s = data.summary;
        summaryDiv.innerHTML = `
            <div class="summary-grid">
                <div class="summary-item">
                    <span class="summary-value">${s.total}</span>
                    <span class="summary-label">总数量</span>
                </div>
                <div class="summary-item benign">
                    <span class="summary-value">${s.class_distribution.benign}</span>
                    <span class="summary-label">良性</span>
                </div>
                <div class="summary-item malignant">
                    <span class="summary-value">${s.class_distribution.malignant}</span>
                    <span class="summary-label">恶性</span>
                </div>
                <div class="summary-item normal">
                    <span class="summary-value">${s.class_distribution.normal}</span>
                    <span class="summary-label">正常</span>
                </div>
            </div>
            <p class="summary-time">总耗时: ${timeMs}ms | 恶性占比: ${(s.malignant_ratio*100).toFixed(1)}%</p>
        `;
        summaryDiv.style.display = 'block';
    }

    // 详细列表
    const detailBody = document.getElementById('batchDetailBody');
    if (detailBody) {
        detailBody.innerHTML = data.results.map(r => `
            <tr class="${r.predicted_class}">
                <td>${r.filename}</td>
                <td>${r.predicted_class_cn}</td>
                <td>${(r.confidence*100).toFixed(2)}%</td>
                <td><div class="mini-bar"><div class="mini-fill ${r.predicted_class}" style="width:${r.confidence*100}%"></div></div></td>
            </tr>
        `).join('');
        document.getElementById('batchDetailTable').style.display = 'table';
    }

    // 隐藏单图区域
    document.getElementById('singleResultCard').style.display = 'none';
    document.getElementById('batchResultCard').style.display = 'block';
}

// ==================== 工具函数 ====================

function formatSize(bytes) {
    if (bytes < 1024) return bytes + 'B';
    if (bytes < 1048576) return (bytes/1024).toFixed(1) + 'KB';
    return (bytes/1048576).toFixed(1) + 'MB';
}
