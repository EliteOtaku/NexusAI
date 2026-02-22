// NexusAI Content Script - Gemini 网页监听器
// 专为 RTX 4080 GPU 优化的 AI 对话捕获系统

class GeminiWatcher {
    constructor() {
        this.lastProcessedText = '';
        this.isProcessing = false;
        this.backendUrl = 'http://localhost:8000/api/v1/ingest';
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
        const nexusBadge = document.createElement('div');
        nexusBadge.id = 'nexus-ai-badge';
        nexusBadge.innerHTML = `
            <div style="
                position: fixed;
                top: 10px;
                right: 10px;
                background: linear-gradient(135deg, #00ff88, #00ccff);
                color: white;
                padding: 8px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: bold;
                z-index: 10000;
                box-shadow: 0 4px 12px rgba(0, 255, 136, 0.3);
                cursor: pointer;
                display: flex;
                align-items: center;
                gap: 6px;
            ">
                <span>🤖 NexusAI</span>
                <span id="nexus-status" style="font-size: 10px; opacity: 0.8;">监听中</span>
            </div>
        `;
        
        nexusBadge.addEventListener('click', () => {
            this.showStatusPopup();
        });
        
        document.body.appendChild(nexusBadge);
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
                this.checkForNewAIResponse(mutation.addedNodes);
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
    
    // 查找 AI 回复元素（Gemini 特定的选择器）
    findAIResponseElements(element) {
        const selectors = [
            // Gemini 新版选择器
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
        
        // 检查是否包含 AI 回复的特征
        const aiIndicators = [
            /(模型|AI|助手|assistant|model)/i,
            /(思考|推理|分析|explain|analyze)/i
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
        const response = await fetch(this.backendUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
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
    }
    
    // 显示错误指示器
    showErrorIndicator(element) {
        this.showIndicator(element, '❌ 同步失败', '#ff4444');
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
        const popup = document.createElement('div');
        popup.innerHTML = `
            <div style="
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: rgba(0, 0, 0, 0.9);
                color: white;
                padding: 20px;
                border-radius: 15px;
                z-index: 10001;
                border: 2px solid #00ff88;
                min-width: 300px;
                text-align: center;
            ">
                <h3 style="margin: 0 0 10px 0; color: #00ff88;">🤖 NexusAI</h3>
                <p style="margin: 5px 0; font-size: 12px;">专为 RTX 4080 优化</p>
                <p style="margin: 10px 0; font-size: 14px;">状态: <span style="color: #00ff88;">监听中</span></p>
                <p style="margin: 5px 0; font-size: 12px; opacity: 0.7;">已捕获: ${this.lastProcessedText ? '1' : '0'} 条对话</p>
                <button onclick="this.parentNode.remove()" style="
                    background: #00ff88;
                    border: none;
                    color: black;
                    padding: 8px 16px;
                    border-radius: 20px;
                    cursor: pointer;
                    margin-top: 10px;
                    font-weight: bold;
                ">关闭</button>
            </div>
        `;
        
        document.body.appendChild(popup);
        
        // 点击外部关闭
        popup.addEventListener('click', (e) => {
            if (e.target === popup) {
                popup.remove();
            }
        });
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