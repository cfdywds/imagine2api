// API 配置
const API_BASE = window.location.origin;
const API_KEY = 'admin';

// 状态管理
let images = [];
let stats = {
    total: 0,
    success: 0,
    failed: 0,
    totalTime: 0
};

// DOM 元素
const generateForm = document.getElementById('generateForm');
const generateBtn = document.getElementById('generateBtn');
const progressContainer = document.getElementById('progressContainer');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const galleryGrid = document.getElementById('galleryGrid');
const clearBtn = document.getElementById('clearBtn');
const modal = document.getElementById('modal');
const modalImage = document.getElementById('modalImage');
const modalClose = document.getElementById('modalClose');
const toast = document.getElementById('toast');

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    loadImages();
    updateStats();
    setupImageToImageListeners();
});

// 设置图生图监听器
function setupImageToImageListeners() {
    // 监听图片上传
    const referenceImage = document.getElementById('referenceImage');
    if (referenceImage) {
        referenceImage.addEventListener('change', (e) => {
            const hasImage = e.target.files.length > 0;
            const modeGroup = document.getElementById('modeGroup');
            const strengthGroup = document.getElementById('strengthGroup');
            const imageCountGroup = document.getElementById('imageCountGroup');

            if (modeGroup) modeGroup.style.display = hasImage ? 'block' : 'none';
            if (strengthGroup) strengthGroup.style.display = hasImage ? 'block' : 'none';
            if (imageCountGroup) imageCountGroup.style.display = hasImage ? 'none' : 'block';

            if (hasImage) {
                generateBtn.textContent = '🎨 图生图';
            } else {
                generateBtn.textContent = '🚀 开始生成';
            }
        });
    }

    // 更新强度显示
    const strengthInput = document.getElementById('strength');
    const strengthValue = document.getElementById('strengthValue');
    if (strengthInput && strengthValue) {
        strengthInput.addEventListener('input', (e) => {
            strengthValue.textContent = e.target.value;
        });
    }
}

// 表单提交
generateForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const prompt = document.getElementById('prompt').value.trim();
    const aspectRatio = document.getElementById('aspectRatio').value;
    const imageCount = parseInt(document.getElementById('imageCount').value);
    const referenceImage = document.getElementById('referenceImage');
    const imageFile = referenceImage ? referenceImage.files[0] : null;

    if (!prompt) {
        showToast('请输入提示词', 'error');
        return;
    }

    // 判断是图生图还是文本生成图片
    if (imageFile) {
        await generateImageToImage(prompt, imageFile, aspectRatio);
    } else {
        await generateImages(prompt, aspectRatio, imageCount);
    }
});

// 生成图片（文本生成图片）
async function generateImages(prompt, aspectRatio, count) {
    generateBtn.disabled = true;
    generateBtn.textContent = '生成中...';
    progressContainer.classList.add('active');

    const startTime = Date.now();

    try {
        // 使用流式 API
        const response = await fetch(`${API_BASE}/v1/chat/completions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${API_KEY}`
            },
            body: JSON.stringify({
                model: 'grok-imagine',
                messages: [{
                    role: 'user',
                    content: prompt
                }],
                stream: true,
                aspect_ratio: aspectRatio,
                n: count
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let imageUrls = [];

        while (true) {
            const { done, value } = await reader.read();

            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop();

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = line.slice(6);

                    if (data === '[DONE]') {
                        break;
                    }

                    try {
                        const json = JSON.parse(data);
                        const delta = json.choices?.[0]?.delta;

                        if (delta?.thinking) {
                            updateProgress(delta.thinking, delta.thinking_progress || 0);
                        }

                        if (delta?.content) {
                            // 提取图片 URL
                            const urlMatches = delta.content.match(/http[s]?:\/\/[^\s\)]+\.jpg/g);
                            if (urlMatches) {
                                imageUrls.push(...urlMatches);
                            }
                        }
                    } catch (e) {
                        console.error('解析 SSE 数据失败:', e);
                    }
                }
            }
        }

        const endTime = Date.now();
        const duration = (endTime - startTime) / 1000;

        if (imageUrls.length > 0) {
            // 保存图片
            for (const url of imageUrls) {
                const image = {
                    id: Date.now() + Math.random(),
                    url: url,
                    prompt: prompt,
                    aspectRatio: aspectRatio,
                    timestamp: Date.now(),
                    duration: duration / imageUrls.length,
                    isImageToImage: false
                };
                images.unshift(image);
            }

            saveImages();
            renderGallery();

            stats.total += imageUrls.length;
            stats.success += imageUrls.length;
            stats.totalTime += duration;
            updateStats();

            showToast(`成功生成 ${imageUrls.length} 张图片！`, 'success');

            // 清空表单
            document.getElementById('prompt').value = '';
        } else {
            throw new Error('未能获取到图片 URL');
        }

    } catch (error) {
        console.error('生成失败:', error);
        stats.total++;
        stats.failed++;
        updateStats();
        showToast(`生成失败: ${error.message}`, 'error');
    } finally {
        generateBtn.disabled = false;
        generateBtn.textContent = '🚀 开始生成';
        progressContainer.classList.remove('active');
        updateProgress('', 0);
    }
}

// 图生图功能
async function generateImageToImage(prompt, imageFile, aspectRatio) {
    generateBtn.disabled = true;
    generateBtn.textContent = '生成中...';
    progressContainer.classList.add('active');

    const mode = document.getElementById('mode').value;
    const strength = parseFloat(document.getElementById('strength').value);
    const startTime = Date.now();

    try {
        const formData = new FormData();
        formData.append('prompt', prompt);
        formData.append('image', imageFile);
        formData.append('mode', mode);
        formData.append('strength', strength);
        formData.append('aspect_ratio', aspectRatio);

        updateProgress('正在上传图片...', 10);

        const response = await fetch(`${API_BASE}/v1/images/edit`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${API_KEY}`
            },
            body: formData
        });

        if (!response.ok) {
            let errorMessage = `HTTP ${response.status}`;
            try {
                const error = await response.json();
                errorMessage = error.detail || errorMessage;
            } catch (e) {
                // 如果无法解析 JSON，使用默认错误消息
            }
            throw new Error(errorMessage);
        }

        updateProgress('正在生成...', 50);

        const result = await response.json();
        const endTime = Date.now();
        const duration = (endTime - startTime) / 1000;

        if (result.data && result.data.length > 0) {
            // 保存结果
            for (const item of result.data) {
                const image = {
                    id: Date.now() + Math.random(),
                    url: item.url,
                    prompt: prompt,
                    mode: mode,
                    aspectRatio: aspectRatio,
                    timestamp: Date.now(),
                    duration: duration,
                    isImageToImage: true
                };
                images.unshift(image);
            }

            saveImages();
            renderGallery();

            stats.total += result.data.length;
            stats.success += result.data.length;
            stats.totalTime += duration;
            updateStats();

            showToast(`图生图成功！`, 'success');

            // 清空表单
            document.getElementById('prompt').value = '';
            document.getElementById('referenceImage').value = '';
            document.getElementById('modeGroup').style.display = 'none';
            document.getElementById('strengthGroup').style.display = 'none';
            document.getElementById('imageCountGroup').style.display = 'block';
            generateBtn.textContent = '🚀 开始生成';
        } else {
            throw new Error('未能获取到图片');
        }

    } catch (error) {
        console.error('图生图失败:', error);
        stats.total++;
        stats.failed++;
        updateStats();
        showToast(`图生图失败: ${error.message}`, 'error');
    } finally {
        generateBtn.disabled = false;
        progressContainer.classList.remove('active');
        updateProgress('', 0);
    }
}

// 更新进度
function updateProgress(text, percent) {
    progressText.textContent = text;
    progressFill.style.width = `${percent}%`;
}

// 渲染画廊
function renderGallery() {
    if (images.length === 0) {
        galleryGrid.innerHTML = `
            <div class="empty-state">
                <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/>
                </svg>
                <h3>还没有生成图片</h3>
                <p>在左侧输入提示词，开始创作吧！</p>
            </div>
        `;
        return;
    }

    galleryGrid.innerHTML = images.map(image => `
        <div class="gallery-item" data-id="${image.id}">
            <img src="${image.url}" alt="${image.prompt}" loading="lazy">
            <div class="gallery-item-info">
                <div class="gallery-item-prompt" title="${image.prompt}">${image.prompt}</div>
                <div class="gallery-item-actions">
                    <button class="download-btn" onclick="downloadImage('${image.url}', '${image.prompt}')">下载</button>
                    <button class="delete-btn" onclick="deleteImage(${image.id})">删除</button>
                </div>
            </div>
        </div>
    `).join('');

    // 添加点击查看大图
    document.querySelectorAll('.gallery-item img').forEach(img => {
        img.addEventListener('click', () => {
            modalImage.src = img.src;
            modal.classList.add('active');
        });
    });
}

// 下载图片
async function downloadImage(url, prompt) {
    try {
        const response = await fetch(url);
        const blob = await response.blob();
        const blobUrl = URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = blobUrl;
        a.download = `${prompt.slice(0, 30)}_${Date.now()}.jpg`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(blobUrl);

        showToast('下载成功！', 'success');
    } catch (error) {
        console.error('下载失败:', error);
        showToast('下载失败', 'error');
    }
}

// 删除图片
function deleteImage(id) {
    if (confirm('确定要删除这张图片吗？')) {
        images = images.filter(img => img.id !== id);
        saveImages();
        renderGallery();
        updateStats();
        showToast('删除成功', 'success');
    }
}

// 清空历史
clearBtn.addEventListener('click', () => {
    if (images.length === 0) {
        showToast('没有图片可清空', 'error');
        return;
    }

    if (confirm(`确定要清空所有 ${images.length} 张图片吗？`)) {
        images = [];
        saveImages();
        renderGallery();
        updateStats();
        showToast('已清空历史', 'success');
    }
});

// 模态框关闭
modalClose.addEventListener('click', () => {
    modal.classList.remove('active');
});

modal.addEventListener('click', (e) => {
    if (e.target === modal) {
        modal.classList.remove('active');
    }
});

// 显示提示
function showToast(message, type = 'success') {
    const toastIcon = document.getElementById('toastIcon');
    const toastMessage = document.getElementById('toastMessage');

    toast.className = `toast ${type} active`;
    toastIcon.textContent = type === 'success' ? '✓' : '✗';
    toastMessage.textContent = message;

    setTimeout(() => {
        toast.classList.remove('active');
    }, 3000);
}

// 更新统计
function updateStats() {
    document.getElementById('totalImages').textContent = stats.total;

    const successRate = stats.total > 0
        ? Math.round((stats.success / stats.total) * 100)
        : 100;
    document.getElementById('successRate').textContent = `${successRate}%`;

    const avgTime = stats.success > 0
        ? Math.round(stats.totalTime / stats.success)
        : 0;
    document.getElementById('avgTime').textContent = `${avgTime}s`;
}

// 保存到 localStorage
function saveImages() {
    try {
        localStorage.setItem('imagine2api_images', JSON.stringify(images));
        localStorage.setItem('imagine2api_stats', JSON.stringify(stats));
    } catch (e) {
        console.error('保存失败:', e);
    }
}

// 从 localStorage 加载
function loadImages() {
    try {
        const savedImages = localStorage.getItem('imagine2api_images');
        const savedStats = localStorage.getItem('imagine2api_stats');

        if (savedImages) {
            images = JSON.parse(savedImages);
            renderGallery();
        }

        if (savedStats) {
            stats = JSON.parse(savedStats);
            updateStats();
        }
    } catch (e) {
        console.error('加载失败:', e);
    }
}

// 键盘快捷键
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + Enter 提交表单
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        if (document.activeElement.id === 'prompt') {
            generateForm.dispatchEvent(new Event('submit'));
        }
    }

    // ESC 关闭模态框
    if (e.key === 'Escape') {
        modal.classList.remove('active');
    }
});
