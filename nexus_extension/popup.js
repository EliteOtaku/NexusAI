// NexusAI Popup Script - 弹窗交互逻辑

class NexusPopup {
    constructor() {
        this.config = {};
        this.init();
    }
    
    async init() {
        console.log('🚀 NexusAI Popup 初始化');
        
        // 加载配置
        await this.loadConfig();
        
        // 更新界面状态
        this.updateUI();
        
        // 检查后端服务状态
        this.checkBackendStatus();
        
        // 绑定事件
        this.bindEvents();
    }
    
    async loadConfig() {
        return new Promise((resolve) => {
            chrome.storage.local.get([
                'nexusEnabled',
                'backendUrl',
                'totalCaptures',
                'lastCapture',
                'cloudMode'
            ], (result) => {
                this.config = result;
                resolve();
            });
        });
    }
    
    updateUI() {
        // 更新扩展状态
        const extensionStatus = document.getElementById('extensionStatus');
        if (this.config.nexusEnabled) {
            extensionStatus.textContent = '已启用';
            extensionStatus.className = 'status-value';
            document.getElementById('toggleBtn').textContent = '禁用捕获';
        } else {
            extensionStatus.textContent = '已禁用';
            extensionStatus.className = 'status-value offline';
            document.getElementById('toggleBtn').textContent = '启用捕获';
        }
        
        // 更新统计数据
        document.getElementById('totalCaptures').textContent = this.config.totalCaptures || 0;
        
        const lastCapture = document.getElementById('lastCapture');
        if (this.config.lastCapture) {
            const date = new Date(this.config.lastCapture);
            lastCapture.textContent = date.toLocaleTimeString();
        } else {
            lastCapture.textContent = '从未';
        }
        
        // 更新云端推理模式
        const cloudMode = this.config.cloudMode || false;
        document.getElementById('cloudModeToggle').checked = cloudMode;
        
        const modeLabel = document.getElementById('modeLabel');
        const modeDescription = document.getElementById('modeDescription');
        
        if (cloudMode) {
            modeLabel.textContent = '云端推理';
            modeDescription.textContent = '☁️ 笔记本省电模式';
        } else {
            modeLabel.textContent = '本地推理';
            modeDescription.textContent = '🚀 RTX 4080 高性能模式';
        }
    }
    
    async checkBackendStatus() {
        const backendStatus = document.getElementById('backendStatus');
        const ollamaStatus = document.getElementById('ollamaStatus');
        
        try {
            // 检查后端健康状态
            const response = await fetch(`${this.config.backendUrl || 'http://localhost:8000'}/api/v1/health`);
            
            if (response.ok) {
                const data = await response.json();
                
                backendStatus.textContent = '在线';
                backendStatus.className = 'status-value';
                
                if (data.ollama && data.ollama.status === 'online') {
                    ollamaStatus.textContent = `在线 (${data.ollama.models?.length || 0} 模型)`;
                    ollamaStatus.className = 'status-value';
                } else {
                    ollamaStatus.textContent = '离线';
                    ollamaStatus.className = 'status-value offline';
                }
            } else {
                throw new Error('HTTP ' + response.status);
            }
            
        } catch (error) {
            console.error('检查后端状态失败:', error);
            
            backendStatus.textContent = '离线';
            backendStatus.className = 'status-value offline';
            
            ollamaStatus.textContent = '未知';
            ollamaStatus.className = 'status-value offline';
        }
    }
    
    bindEvents() {
        // 切换捕获模式
        document.getElementById('toggleBtn').addEventListener('click', () => {
            this.toggleCaptureMode();
        });
        
        // 打开设置页面
        document.getElementById('settingsBtn').addEventListener('click', () => {
            chrome.tabs.create({
                url: chrome.runtime.getURL('options.html')
            });
        });
        
        // 切换云端推理模式
        document.getElementById('cloudModeToggle').addEventListener('change', (event) => {
            this.toggleCloudMode(event.target.checked);
        });
        
        // 刷新按钮（双击标题）
        document.querySelector('h1').addEventListener('dblclick', () => {
            this.refreshStatus();
        });
    }
    
    async toggleCaptureMode() {
        const newState = !this.config.nexusEnabled;
        
        await new Promise((resolve) => {
            chrome.storage.local.set({ nexusEnabled: newState }, () => {
                this.config.nexusEnabled = newState;
                resolve();
            });
        });
        
        this.updateUI();
        
        // 发送消息到内容脚本
        chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
            if (tabs[0]) {
                chrome.tabs.sendMessage(tabs[0].id, {
                    action: 'toggleCapture',
                    enabled: newState
                });
            }
        });
        
        // 显示通知
        this.showNotification(newState ? '捕获模式已启用' : '捕获模式已禁用');
    }
    
    async refreshStatus() {
        const backendStatus = document.getElementById('backendStatus');
        const ollamaStatus = document.getElementById('ollamaStatus');
        
        backendStatus.innerHTML = '检查中<span class="loading"></span>';
        ollamaStatus.innerHTML = '检查中<span class="loading"></span>';
        
        await this.loadConfig();
        this.updateUI();
        await this.checkBackendStatus();
        
        this.showNotification('状态已刷新');
    }
    
    async toggleCloudMode(enabled) {
        await new Promise((resolve) => {
            chrome.storage.local.set({ cloudMode: enabled }, () => {
                this.config.cloudMode = enabled;
                resolve();
            });
        });
        
        this.updateUI();
        
        const mode = enabled ? '云端推理' : '本地推理';
        const description = enabled ? '笔记本省电模式已启用' : 'RTX 4080 高性能模式已启用';
        
        this.showNotification(`${mode}: ${description}`);
        
        // 发送消息到内容脚本
        chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
            if (tabs[0]) {
                chrome.tabs.sendMessage(tabs[0].id, {
                    action: 'cloudModeChanged',
                    enabled: enabled
                });
            }
        });
    }
    
    showNotification(message) {
        // 创建临时通知元素
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 10px;
            left: 50%;
            transform: translateX(-50%);
            background: #00ff88;
            color: black;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            z-index: 1000;
            animation: slideDown 0.3s ease;
        `;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 2000);
    }
    
    loadRecentCaptures() {
        // 这里可以加载最近的捕获记录
        // 目前先显示静态信息
        const capturesList = document.getElementById('capturesList');
        
        if (this.config.totalCaptures > 0) {
            capturesList.innerHTML = `
                <div class="capture-item">最后捕获: ${this.config.lastCapture ? new Date(this.config.lastCapture).toLocaleString() : '未知'}</div>
                <div class="capture-item">总计: ${this.config.totalCaptures} 条对话</div>
            `;
        }
    }
}

// 添加 CSS 动画
const style = document.createElement('style');
style.textContent = `
    @keyframes slideDown {
        from { transform: translate(-50%, -20px); opacity: 0; }
        to { transform: translate(-50%, 0); opacity: 1; }
    }
`;
document.head.appendChild(style);

// 初始化弹窗
document.addEventListener('DOMContentLoaded', () => {
    new NexusPopup();
});