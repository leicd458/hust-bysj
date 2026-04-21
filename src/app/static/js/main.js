/**
 * 前端交互逻辑 - 重构版
 * 单图分析 / TTA增强 / 批量分析（逐张进度 + 卡片式结果 + 可展开详情）
 */

let selectedFile = null;
let selectedFiles = [];
let originalImageBase64 = null;
let useTTA = true;
let batchMode = false;       // 'single' | 'batch'
let batchResults = [];      // 保存批量结果，支持展开查看

/* ==================== 初始化 ==================== */
function initApp() {
    const uploadArea = document.getElementById('uploadArea');
    const imageInput = document.getElementById('imageInput');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const changeImageBtn = document.getElementById('changeImage');
    const ttaToggle = document.getElementById('ttaToggle');

    if (uploadArea) uploadArea.addEventListener('click', (e) => {
        if (!e.target.closest('.btn-secondary') && !e.target.closest('.btn-add-more')) imageInput.click();
    });

    imageInput.addEventListener('change', handleFileSelect);

    if (uploadArea) {
        uploadArea.addEventListener('dragover', e => { e.preventDefault(); uploadArea.classList.add('drag-over'); });
        uploadArea.addEventListener('dragleave', () => uploadArea.classList.remove('drag-over'));
        uploadArea.addEventListener('drop', e => {
            e.preventDefault();
            uploadArea.classList.remove('drag-over');
            const files = Array.from(e.dataTransfer.files);
            if (files.length > 0) {
                if (batchMode === 'batch') handleBatchFiles(files);
                else handleFile(files[0]);
            }
        });
    }

    if (analyzeBtn) analyzeBtn.addEventListener('click', analyzeImage);
    if (changeImageBtn) {
        changeImageBtn.addEventListener('click', e => { e.stopPropagation(); imageInput.click(); });
    }
    if (ttaToggle) ttaToggle.addEventListener('change', () => { useTTA = ttaToggle.checked; updateTTALabel(); });
    updateTTALabel();
}

function updateTTALabel() {
    const el = document.getElementById('ttaLabel');
    if (el) el.textContent = useTTA ? 'TTA 增强推理（推荐）' : '标准推理';
}

/* ==================== 模式切换 ==================== */
function switchMode(mode) {
    batchMode = mode;
    document.getElementById('singleModeBtn').classList.toggle('active', mode === 'single');
    document.getElementById('batchModeBtn').classList.toggle('active', mode === 'batch');
    document.getElementById('imageInput').multiple = (mode === 'batch');
    document.getElementById('analyzeBtnText').textContent =
        mode === 'batch' ? '&#128202; 批量分析' : '&#128269; 开始分析';
    resetUpload();
}

/* ==================== 文件处理 ==================== */
function handleFileSelect(e) {
    const files = Array.from(e.target.files);
    if (!files.length) return;
    if (batchMode === 'batch') handleBatchFiles(files);
    else handleFile(files[0]);
}

function handleFile(file) {
    if (!validateFile(file)) return;
    selectedFile = file;

    // 更新提示文字
    const hintEl = document.getElementById('uploadHintText');
    if (hintEl) hintEl.textContent = '点击或拖拽图像到此处';

    const reader = new FileReader();
    reader.onload = (e) => {
        originalImageBase64 = e.target.result;
        const previewImage = document.getElementById('previewImage');
        if (previewImage) { previewImage.src = e.target.result; previewImage.alt = file.name; }
        document.getElementById('uploadPlaceholder').style.display = 'none';
        document.getElementById('previewContainer').style.display = 'flex';
        document.getElementById('analyzeBtn').disabled = false;
    };
    reader.readAsDataURL(file);
    document.getElementById('resultSection').style.display = 'none';
}

function handleBatchFiles(fileList) {
    const newFiles = Array.from(fileList).filter(f => validateFile(f, true));
    if (!newFiles.length) return;

    // 合并已有文件（去重）
    const existingNames = selectedFiles.map(f => f.name);
    for (const f of newFiles) {
        if (!existingNames.includes(f.name)) selectedFiles.push(f);
    }

    // 上限检查
    if (selectedFiles.length > 10) {
        alert('最多支持 10 张图片，已截断。');
        selectedFiles = selectedFiles.slice(0, 10);
    }

    renderBatchPreview();
    document.getElementById('uploadPlaceholder').style.display = 'none';
    document.getElementById('previewContainer').style.display = 'none';
    document.getElementById('batchPreviewContainer').style.display = 'block';
    document.getElementById('analyzeBtn').disabled = false;
}

function renderBatchPreview() {
    const grid = document.getElementById('batchPreviewGrid');
    const countEl = document.getElementById('batchCount');
    countEl.textContent = selectedFiles.length;

    grid.innerHTML = selectedFiles.map((f, i) => `
        <div class="batch-thumb-card">
            <div class="thumb-preview">
                <img src="" data-index="${i}" alt="${f.name}" onload="this.style.opacity=1" onerror="this.parentElement.innerHTML='<span class=thumb-placeholder>IMG</span>'">
                <button class="thumb-remove" onclick="removeBatchItem(${i})" title="移除">&times;</button>
            </div>
            <div class="thumb-info">
                <span class="thumb-name">${f.name}</span>
                <span class="thumb-size">${formatSize(f.size)}</span>
            </div>
        </div>
    `).join('');

    // 异步读取缩略图
    selectedFiles.forEach((f, i) => {
        const reader = new FileReader();
        reader.onload = e => {
            const img = grid.querySelector(`img[data-index="${i}"]`);
            if (img) img.src = e.target.result;
        };
        reader.readAsDataURL(f);
    });
}

// 继续添加按钮
document.addEventListener('DOMContentLoaded', () => {
    const addMoreBtn = document.getElementById('addMoreBtn');
    if (addMoreBtn) addMoreBtn.addEventListener('click', e => { e.stopPropagation(); document.getElementById('imageInput').click(); });
});

function removeBatchItem(index) {
    selectedFiles.splice(index, 1);
    if (selectedFiles.length === 0) { resetUpload(); }
    else renderBatchPreview();
}

function resetUpload() {
    selectedFile = null;
    selectedFiles = [];
    batchResults = [];
    originalImageBase64 = null;
    const previewContainer = document.getElementById('previewContainer');
    const uploadPlaceholder = document.getElementById('uploadPlaceholder');
    const batchPreviewContainer = document.getElementById('batchPreviewContainer');
    const resultSection = document.getElementById('resultSection');
    const progressWrap = document.getElementById('progressWrap');

    if (previewContainer) previewContainer.style.display = 'none';
    if (uploadPlaceholder) uploadPlaceholder.style.display = 'flex';
    if (batchPreviewContainer) batchPreviewContainer.style.display = 'none';
    if (resultSection) resultSection.style.display = 'none';
    if (progressWrap) progressWrap.style.display = 'none';

    const hintEl = document.getElementById('uploadHintText');
    if (hintEl) hintEl.textContent = '点击或拖拽图像到此处';

    const analyzeBtn = document.getElementById('analyzeBtn');
    if (analyzeBtn) analyzeBtn.disabled = true;

    const imageInput = document.getElementById('imageInput');
    if (imageInput) imageInput.value = '';
}

/* ==================== 验证 & 分析 ==================== */
function validateFile(file, silent=false) {
    const allowedExts = ['.png','.jpg','.jpeg','.bmp'];
    const ext = '.' + file.name.split('.').pop().toLowerCase();
    if (!allowedExts.includes(ext)) {
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
    const analyzeBtn = document.getElementById('analyzeBtn');
    const btnText = analyzeBtn.querySelector('#analyzeBtnText');
    const btnLoading = analyzeBtn.querySelector('.btn-loading');
    const progressWrap = document.getElementById('progressWrap');

    btnText.style.display = 'none';
    btnLoading.style.display = 'inline-flex';
    analyzeBtn.disabled = true;

    try {
        if (batchMode === 'batch' && selectedFiles.length > 1) {
            await runBatchAnalysis(progressWrap);
        } else {
            await runSingleAnalysis();
        }
    } catch (error) {
        console.error(error);
        alert('分析失败: ' + error.message);
    } finally {
        btnText.style.display = 'inline';
        btnLoading.style.display = 'none';
        analyzeBtn.disabled = false;
        progressWrap.style.display = 'none';
    }
}

/* ==================== 单图分析 ==================== */
async function runSingleAnalysis() {
    const endpoint = useTTA ? '/predict_tta' : '/predict';
    const formData = new FormData();
    formData.append('file', selectedFile || selectedFiles[0]);

    const t0 = performance.now();
    const resp = await fetch(endpoint, { method: 'POST', body: formData });
    const data = await resp.json();
    const elapsed = (performance.now() - t0).toFixed(0);

    if (!data.success) throw new Error(data.error || '未知错误');
    displayResult(data.result, elapsed);
}

/* ==================== 批量分析（逐张 + 进度条）==================== */
async function runBatchAnalysis(progressWrap) {
    batchResults = [];
    const total = selectedFiles.length;
    const progressFill = document.getElementById('progressFill');
    const progressLabel = document.getElementById('progressLabel');
    const progressPct = document.getElementById('progressPct');

    progressWrap.style.display = 'block';

    for (let i = 0; i < total; i++) {
        const f = selectedFiles[i];
        progressLabel.textContent = `正在分析 ${i + 1}/${total}: ${f.name}`;

        const formData = new FormData();
        formData.append('file', f);

        try {
            const t0 = performance.now();
            const resp = await fetch('/predict_tta', { method: 'POST', body: formData });
            const data = await resp.json();
            const elapsed = Math.round(performance.now() - t0);

            if (data.success) {
                batchResults.push({
                    ...data.result,
                    filename: f.name,
                    elapsed_ms: elapsed,
                    index: i
                });
            } else {
                batchResults.push({ filename: f.name, error: data.error || '分析失败', elapsed_ms: 0, index: i });
            }
        } catch (err) {
            batchResults.push({ filename: f.name, error: err.message, elapsed_ms: 0, index: i });
        }

        // 更新进度
        const pct = Math.round(((i + 1) / total) * 100);
        progressFill.style.width = pct + '%';
        progressPct.textContent = pct + '%';
    }

    displayBatchResult();
}

/* ==================== 结果展示：单图 ==================== */
function displayResult(result, timeMs=0) {
    const section = document.getElementById('resultSection');
    section.style.display = 'block';
    section.scrollIntoView({ behavior: 'smooth' });

    const cls = document.getElementById('diagnosisClass');
    cls.textContent = result.predicted_class_cn || '-';
    cls.className = 'diagnosis-class ' + (result.predicted_class || '');

    document.getElementById('confidenceValue').textContent = (result.confidence * 100).toFixed(2) + '%';

    ['benign','malignant','normal'].forEach(name => {
        const pct = (result.probabilities[name] * 100).toFixed(2);
        const cap = name.charAt(0).toUpperCase() + name.slice(1);
        document.getElementById(`prob${cap}`).style.width = pct + '%';
        document.getElementById(`prob${cap}Value`).textContent = pct + '%';
    });

    const origImg = document.getElementById('originalImage');
    const camImg = document.getElementById('gradcamImage');
    origImg.src = originalImageBase64;
    origImg.style.display = 'block';
    camImg.src = result.gradcam || '';
    camImg.style.display = result.gradcam ? 'block' : 'none';

    const infoEl = document.getElementById('inferenceInfo');
    if (infoEl) infoEl.textContent = `${timeMs}ms | ${useTTA ? 'TTA' : '标准'}`;
}

/* ==================== 结果展示：批量（卡片列表+展开详情）==================== */
function displayBatchResult() {
    const section = document.getElementById('resultSection');
    section.style.display = 'block';
    section.scrollIntoView({ behavior: 'smooth' });

    document.getElementById('singleResultCard').style.display = 'none';
    document.getElementById('batchResultCard').style.display = 'block';

    // 统计摘要
    const stats = { benign: 0, malignant: 0, normal: 0, errors: 0 };
    batchResults.forEach(r => {
        if (r.error) stats.errors++;
        else stats[r.predicted_class] = (stats[r.predicted_class] || 0) + 1;
    });

    const summaryGrid = document.getElementById('batchSummaryGrid');
    const totalOk = batchResults.length - stats.errors;
    summaryGrid.innerHTML = `
        <div class="summary-item"><span class="summary-value">${batchResults.length}</span><span class="summary-label">总数量</span></div>
        <div class="summary-item benign"><span class="summary-value">${stats.benign}</span><span class="summary-label">良性</span></div>
        <div class="summary-item malignant"><span class="summary-value">${stats.malignant}</span><span class="summary-label">恶性</span></div>
        <div class="summary-item normal"><span class="summary-value">${stats.normal}</span><span class="summary-label">正常</span></div>
    `;
    if (stats.errors > 0) {
        summaryGrid.innerHTML += `<div class="summary-item" style="background:#fef2f2"><span class="summary-value" style="color:#dc2626">${stats.errors}</span><span class="summary-label">失败</span></div>`;
    }

    // 结果卡片列表
    const listEl = document.getElementById('batchResultsList');
    listEl.innerHTML = '';

    batchResults.forEach((r, idx) => {
        const hasError = !!r.error;
        const cls = r.predicted_class || '';
        const clsCN = r.predicted_class_cn || '-';
        const conf = r.confidence ? (r.confidence*100).toFixed(1) : '-';

        const card = document.createElement('div');
        card.className = `bresult-card ${hasError ? 'has-error' : ''} ${cls}`;
        card.innerHTML = `
            <div class="bresult-header" onclick="toggleBResultDetail(${idx})">
                <div class="bresult-left">
                    <span class="bresult-num">#${idx + 1}</span>
                    <div class="bresult-file-info">
                        <span class="bresult-filename">${r.filename}</span>
                        <span class="bresult-time">${r.elapsed_ms}ms</span>
                    </div>
                </div>
                <div class="bresult-right">
                    ${hasError
                        ? '<span class="bresult-badge error-badge">分析失败</span>'
                        : `<span class="bresult-badge ${cls}-badge">${clsCN}</span>`
                    }
                    ${!hasError ? `<span class="bresult-conf">${conf}%</span>` : ''}
                    <span class="bresult-arrow" id="arrow${idx}">&#9660;</span>
                </div>
            </div>
            <div class="bresult-detail" id="detail${idx}" style="display:none;">
                ${hasError
                    ? `<p class="error-msg">${r.error}</p>`
                    : `
                        <div class="bresult-probs">
                            ${['benign','malignant','normal'].map(n =>
                                `<div class="bresult-prob-row">
                                    <span>${n==='benign'? '良性': n==='malignant'? '恶性':'正常'}</span>
                                    <div class="bresult-prob-bar-wrap"><div class="bresult-prob-bar bresult-${n}" style="width:${(r.probabilities[n]*100).toFixed(1)}%"></div></div>
                                    <span>${(r.probabilities[n]*100).toFixed(1)}%</span>
                                </div>`
                            ).join('')}
                        </div>

                        ${r.gradcam
                            ? `<div class="bresult-cam">
                                <h5>Grad-CAM 热力图</h5>
                                <img src="${r.gradcam}" alt="Grad-CAM" loading="lazy">
                              </div>`
                            : ''
                        }
                      `
                }
            </div>
        `;
        listEl.appendChild(card);

        // 预加载缩略图用于详情展示
        if (!hasError && selectedFiles[idx]) {
            const reader = new FileReader();
            reader.onload = (e) => {
                // 缓存 base64 到结果对象
                batchResults[idx]._thumbBase64 = e.target.result;
            };
            reader.readAsDataURL(selectedFiles[idx]);
        }
    });
}

function toggleBResultDetail(idx) {
    const detailEl = document.getElementById('detail' + idx);
    const arrowEl = document.getElementById('arrow' + idx);
    const isOpen = detailEl.style.display !== 'none';

    detailEl.style.display = isOpen ? 'none' : 'block';
    arrowEl.textContent = isOpen ? '\u25BC' : '\u25B2';
    arrowEl.style.transform = isOpen ? '' : 'rotate(180deg)';
}

function clearBatchResults() {
    if (!confirm('确定清空所有结果？')) return;
    batchResults = [];
    document.getElementById('resultSection').style.display = 'none';
    resetUpload();
}

function exportBatchReport() {
    // 简单导出为文本摘要
    const lines = ['乳腺癌超声诊断 - 批量分析报告', '=' .repeat(40), ''];
    lines.push(`时间: ${new Date().toLocaleString()}`);
    lines.push(`总数: ${batchResults.length}`);
    lines.push('');
    batchResults.forEach((r, i) => {
        if (r.error) {
            lines.push(`#${i+1} ${r.filename} - 失败: ${r.error}`);
        } else {
            lines.push(`#${i+1} ${r.filename} - ${r.predicted_class_cn} (${(r.confidence*100).toFixed(1)}%)`);
        }
    });

    const blob = new Blob([lines.join('\n')], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = `batch_report_${Date.now()}.txt`; a.click();
    URL.revokeObjectURL(url);
}

/* ==================== 工具函数 ==================== */
function formatSize(bytes) {
    if (bytes < 1024) return bytes + 'B';
    if (bytes < 1048576) return (bytes/1024).toFixed(1) + 'KB';
    return (bytes/1048576).toFixed(1) + 'MB';
}
