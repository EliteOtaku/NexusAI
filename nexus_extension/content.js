// NexusAI Content Script - Gemini 网页监听器
// 专为 RTX 4080 GPU 优化的 AI 对话捕获系统

class GeminiWatcher {
    constructor() {
        this.lastProcessedText = '';
        this.isProcessing = false;
        this.backendUrl = 'http://127.0.0.1:8000/api/v1/ingest';
        this.observer = null;
        
        this.init();
    }
    
    init() {
        console.log('🔍 NexusAI: 开始监听 Gemini 对话...');
        this.injectNexusUI();
        this.startObservation();
        this.setupMessageListener();
    }
    
    // 注入 NexusAI UI 元素
    injectNexusUI() {
        // 添加闪烁动画样式
        if (!document.querySelector('#nexus-flash-animation')) {
            const style = document.createElement('style');
            style.id = 'nexus-flash-animation';
            style.textContent = `
                @keyframes nexusFlash {
                    0% { transform: scale(1); box-shadow: 0 4px 12px rgba(0, 255, 136, 0.3); }
                    50% { transform: scale(1.1); box-shadow: 0 6px 20px rgba(0, 255, 136, 0.6); }
                    100% { transform: scale(1); box-shadow: 0 4px 12px rgba(0, 255, 136, 0.3); }
                }
            `;
            document.head.appendChild(style);
        }
        
        const nexusBadge = document.createElement('div');
        nexusBadge.id = 'nexus-ai-badge';
        // 使用顶级 z-index 确保不被遮挡
        nexusBadge.style.cssText = `
            position: fixed; top: 20px; right: 20px; z-index: 2147483647; 
            cursor: move; user-select: none; 
        `;
        
        nexusBadge.innerHTML = `
            <div id="nexus-drag-handle" style="
                background: linear-gradient(135deg, #00ff88, #00ccff);
                color: white; padding: 10px 16px; border-radius: 25px;
                font-family: sans-serif; font-weight: bold; font-size: 13px;
                display: flex; align-items: center; gap: 8px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.3);
                transition: all 0.3s ease;
            ">
                <span>🤖 NexusAI</span>
                <span id="nexus-status" style="font-size: 11px; opacity: 0.9;">监听中</span>
            </div>
        `;
        
        document.body.appendChild(nexusBadge);
        this.makeDraggable(nexusBadge);
        
        // 点击非拖拽区域打开弹窗
        nexusBadge.addEventListener('click', (e) => {
            if (!this.isDragging) this.showStatusPopup();
        });
    }
    
    // 开始观察 DOM 变化
    startObservation() {
        const observerConfig = {
            childList: true,
            subtree: true,
            characterData: true
        };
        
        this.observer = new MutationObserver((mutations) => {
            this.handleMutations(mutations);
        });
        
        this.observer.observe(document.body, observerConfig);
    }
    
    // 处理 DOM 变化
    handleMutations(mutations) {
        for (const mutation of mutations) {
            if (mutation.type === 'childList') {
                // 对于 DeepSeek 的流式输出，延迟检查以确保文本完整
                setTimeout(() => {
                    this.checkForNewAIResponse(mutation.addedNodes);
                }, 500); // 500ms 延迟，确保流式输出完成
            }
        }
    }
    
    // 检查新的 AI 回复
    checkForNewAIResponse(nodes) {
        for (const node of nodes) {
            if (node.nodeType === Node.ELEMENT_NODE) {
                // 查找 Gemini 的 AI 回复元素
                const aiResponses = this.findAIResponseElements(node);
                
                for (const response of aiResponses) {
                    this.processAIResponse(response);
                }
            }
        }
    }
    
    // 查找 AI 回复元素（支持 Gemini 和 DeepSeek）
    findAIResponseElements(element) {
        const selectors = [
            // DeepSeek 专用选择器
            '.ds-markdown',
            '.ds-chat-bubble',
            '[class*="ds-"]:last-child',
            // Gemini 专用选择器
            '[data-testid="conversation-turn"]:last-child model-response',
            '.model-response',
            '.ai-response',
            '[class*="response"]',
            '[class*="message"]:last-child',
            // 通用选择器
            'div[role="document"] div:last-child',
            'div[contenteditable="false"]'
        ];
        
        const responses = [];
        
        for (const selector of selectors) {
            const elements = element.querySelectorAll ? element.querySelectorAll(selector) : [];
            for (const el of elements) {
                if (this.isAIResponse(el)) {
                    responses.push(el);
                }
            }
        }
        
        return responses;
    }
    
    // 判断是否为 AI 回复
    isAIResponse(element) {
        const text = element.textContent?.trim() || '';
        
        // 排除空内容或用户输入
        if (!text || text.length < 10) return false;
        
        // DeepSeek 特定识别（基于类名）
        if (element.classList?.contains('ds-markdown') || 
            element.classList?.contains('ds-chat-bubble') ||
            element.className?.includes('ds-')) {
            return true;
        }
        
        // 检查是否包含 AI 回复的特征
        const aiIndicators = [
            /(模型|AI|助手|assistant|model)/i,
            /(思考|推理|分析|explain|analyze)/i,
            /(DeepSeek|deepseek)/i,
            /(作为.*AI|作为.*助手)/i
        ];
        
        return aiIndicators.some(indicator => indicator.test(text));
    }
    
    // 处理 AI 回复
    async processAIResponse(responseElement) {
        if (this.isProcessing) return;
        
        const text = responseElement.textContent?.trim() || '';
        
        // 去重检查
        if (!text || text === this.lastProcessedText || text.length < 20) {
            return;
        }
        
        this.isProcessing = true;
        this.lastProcessedText = text;
        
        // 调试信息：显示命中的元素
        console.log('🎯 命中元素:', responseElement);
        console.log('🎯 元素类名:', responseElement.className);
        console.log('🎯 元素标签:', responseElement.tagName);
        console.log('🤖 NexusAI: 检测到新的 AI 回复:', text.substring(0, 100) + '...');
        
        // 更新 UI 状态
        this.updateStatus('捕获中...');
        
        try {
            await this.sendToBackend({
                source: 'gemini',
                content: text,
                url: window.location.href,
                timestamp: new Date().toISOString(),
                element_html: responseElement.outerHTML.substring(0, 1000)
            });
            
            this.updateStatus('已同步');
            this.showSuccessIndicator(responseElement);
            
        } catch (error) {
            console.error('❌ NexusAI: 发送失败:', error);
            this.updateStatus('同步失败');
            this.showErrorIndicator(responseElement);
        }
        
        this.isProcessing = false;
    }
    
    // 发送数据到后端
    async sendToBackend(data) {
        try {
            const response = await fetch(this.backendUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error(`❌ NexusAI: 后端响应异常 (${response.status})`, errorText);
                throw new Error(`HTTP ${response.status}: ${response.statusText} - ${errorText}`);
            }
            
            const result = await response.json();
            console.log('✅ NexusAI: 数据同步成功', result);
            return result;
            
        } catch (error) {
            console.error('❌ NexusAI: 网络请求失败', {
                url: this.backendUrl,
                error: error.message,
                data: data
            });
            throw error;
        }
    }
    
    // 更新状态显示
    updateStatus(status) {
        const statusElement = document.getElementById('nexus-status');
        if (statusElement) {
            statusElement.textContent = status;
            
            // 根据状态改变颜色
            if (status === '已同步') {
                statusElement.style.color = '#00ff88';
            } else if (status === '同步失败') {
                statusElement.style.color = '#ff4444';
            } else {
                statusElement.style.color = '#ffffff';
            }
        }
    }
    
    // 显示成功指示器
    showSuccessIndicator(element) {
        this.showIndicator(element, '✅ NexusAI 已捕获', '#00ff88');
        this.flashBadge();
    }
    
    // 显示错误指示器
    showErrorIndicator(element) {
        this.showIndicator(element, '❌ 同步失败', '#ff4444');
        console.error('❌ NexusAI: 同步失败详情', {
            element: element,
            text: element.textContent?.substring(0, 200),
            url: window.location.href
        });
    }
    
    // 显示指示器
    showIndicator(element, text, color) {
        const indicator = document.createElement('div');
        indicator.innerHTML = `
            <div style="
                position: absolute;
                top: -30px;
                right: 10px;
                background: ${color};
                color: white;
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 10px;
                font-weight: bold;
                z-index: 1000;
                animation: fadeInOut 2s ease-in-out;
            ">${text}</div>
        `;
        
        // 添加 CSS 动画
        if (!document.querySelector('#nexus-animations')) {
            const style = document.createElement('style');
            style.id = 'nexus-animations';
            style.textContent = `
                @keyframes fadeInOut {
                    0% { opacity: 0; transform: translateY(10px); }
                    20% { opacity: 1; transform: translateY(0); }
                    80% { opacity: 1; transform: translateY(0); }
                    100% { opacity: 0; transform: translateY(-10px); }
                }
            `;
            document.head.appendChild(style);
        }
        
        element.style.position = 'relative';
        element.appendChild(indicator);
        
        // 2秒后移除指示器
        setTimeout(() => {
            if (indicator.parentNode) {
                indicator.parentNode.removeChild(indicator);
            }
        }, 2000);
    }
    
    // 显示状态弹窗
    showStatusPopup() {
        // 先清理旧的，防止"关不掉"
        const oldPopup = document.getElementById('nexus-popup-overlay');
        if (oldPopup) oldPopup.remove();

        const overlay = document.createElement('div');
        overlay.id = 'nexus-popup-overlay';
        overlay.style.cssText = `
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.7); z-index: 2147483647;
            display: flex; align-items: center; justify-content: center;
            backdrop-filter: blur(4px);
        `;

        overlay.innerHTML = `
            <div style="background: #1a1a1a; border: 2px solid #00ff88; padding: 25px; border-radius: 15px; color: white; min-width: 320px; text-align: center;">
                <h2 style="color: #00ff88; margin-bottom: 15px;">至尊魔戒控制台</h2>
                <div style="margin-bottom: 20px; font-size: 14px;">
                    <p>算力核心: <span style="color: #00ccff;">RTX 4080</span></p>
                    <p>当前状态: <span style="color: #00ff88;">✅ 正常运转</span></p>
                    <p>已捕获对话: <span style="color: #00ff88;">${this.lastProcessedText ? '1' : '0'}</span> 条</p>
                    <p>监听平台: <span style="color: #00ccff;">Gemini & DeepSeek</span></p>
                </div>
                <button id="nexus-close-btn" style="background: #00ff88; color: black; border: none; padding: 10px 30px; border-radius: 5px; cursor: pointer; font-weight: bold;">
                    关闭
                </button>
            </div>
        `;

        document.body.appendChild(overlay);

        // 强力绑定关闭事件
        document.getElementById('nexus-close-btn').addEventListener('click', (e) => {
            e.stopPropagation();
            overlay.remove();
        });
        
        // 点击外部关闭
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                overlay.remove();
            }
        });
    }
    
    // 🚀 核心：拖拽功能实现
    makeDraggable(el) {
        let pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
        this.isDragging = false;

        el.onmousedown = (e) => {
            e.preventDefault();
            this.isDragging = false;
            pos3 = e.clientX;
            pos4 = e.clientY;
            document.onmouseup = () => {
                document.onmouseup = null;
                document.onmousemove = null;
                setTimeout(() => this.isDragging = false, 100);
            };
            document.onmousemove = (e) => {
                this.isDragging = true;
                pos1 = pos3 - e.clientX;
                pos2 = pos4 - e.clientY;
                pos3 = e.clientX;
                pos4 = e.clientY;
                el.style.top = (el.offsetTop - pos2) + "px";
                el.style.left = (el.offsetLeft - pos1) + "px";
                el.style.right = 'auto'; // 覆盖初始的 right: 20px
            };
        };
    }

    // 气泡闪烁效果
    flashBadge() {
        const badge = document.getElementById('nexus-ai-badge');
        if (badge) {
            badge.style.animation = 'nexusFlash 0.5s ease-in-out';
            setTimeout(() => {
                badge.style.animation = '';
            }, 500);
        }
    }
    
    // 设置消息监听器
    setupMessageListener() {
        chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
            if (request.action === 'getStatus') {
                sendResponse({
                    status: 'active',
                    lastProcessed: this.lastProcessedText.substring(0, 100),
                    url: window.location.href
                });
            }
        });
    }
}

// 初始化监听器
const geminiWatcher = new GeminiWatcher();

// 导出供测试使用
window.NexusAI = geminiWatcher;