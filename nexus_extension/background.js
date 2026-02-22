// NexusAI Background Script - 服务工作者
// 专为 RTX 4080 优化的浏览器扩展后台服务

console.log('🚀 NexusAI Background Script 已启动');

// 监听扩展安装事件
chrome.runtime.onInstalled.addListener((details) => {
    console.log('NexusAI 扩展已安装:', details.reason);
    
    if (details.reason === 'install') {
        // 首次安装时显示欢迎页面
        chrome.tabs.create({
            url: chrome.runtime.getURL('welcome.html')
        });
    }
    
    // 设置默认配置
    chrome.storage.local.set({
        nexusEnabled: true,
        backendUrl: 'http://localhost:8000',
        targetSites: ['gemini.google.com'],
        captureMode: 'auto',
        lastCapture: null,
        totalCaptures: 0
    });
});

// 监听标签页更新
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.url.includes('gemini.google.com')) {
        console.log('🔍 检测到 Gemini 页面加载完成');
        
        // 注入内容脚本
        chrome.scripting.executeScript({
            target: { tabId: tabId },
            files: ['content.js']
        }).then(() => {
            console.log('✅ NexusAI 内容脚本已注入');
        }).catch(err => {
            console.error('❌ 注入内容脚本失败:', err);
        });
    }
});

// 监听来自内容脚本的消息
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log('📨 收到消息:', request);
    
    switch (request.action) {
        case 'captureSuccess':
            handleCaptureSuccess(request.data);
            break;
            
        case 'captureError':
            handleCaptureError(request.data);
            break;
            
        case 'getConfig':
            sendResponse(getConfig());
            break;
            
        case 'updateConfig':
            updateConfig(request.config);
            sendResponse({ success: true });
            break;
    }
    
    return true; // 保持消息通道开放
});

// 处理捕获成功
async function handleCaptureSuccess(data) {
    console.log('✅ AI 回复捕获成功:', data);
    
    // 更新统计数据
    const result = await chrome.storage.local.get(['totalCaptures']);
    const totalCaptures = (result.totalCaptures || 0) + 1;
    
    await chrome.storage.local.set({
        lastCapture: new Date().toISOString(),
        totalCaptures: totalCaptures
    });
    
    // 显示桌面通知（如果用户允许）
    showCaptureNotification(data);
}

// 处理捕获错误
function handleCaptureError(error) {
    console.error('❌ AI 回复捕获失败:', error);
    
    // 显示错误通知
    chrome.notifications.create({
        type: 'basic',
        iconUrl: 'icons/icon48.png',
        title: 'NexusAI 捕获失败',
        message: error.message || '未知错误',
        priority: 2
    });
}

// 显示捕获通知
function showCaptureNotification(data) {
    chrome.notifications.create({
        type: 'basic',
        iconUrl: 'icons/icon48.png',
        title: 'NexusAI 已捕获 AI 回复',
        message: `来自 ${data.source} 的对话已同步`,
        priority: 1
    });
}

// 获取配置
async function getConfig() {
    const result = await chrome.storage.local.get([
        'nexusEnabled',
        'backendUrl',
        'targetSites',
        'captureMode',
        'lastCapture',
        'totalCaptures'
    ]);
    
    return result;
}

// 更新配置
async function updateConfig(newConfig) {
    await chrome.storage.local.set(newConfig);
    console.log('⚙️ 配置已更新:', newConfig);
}

// 监听键盘快捷键
chrome.commands.onCommand.addListener((command) => {
    console.log('⌨️ 快捷键触发:', command);
    
    switch (command) {
        case 'toggle-capture':
            toggleCaptureMode();
            break;
        case 'open-dashboard':
            openDashboard();
            break;
    }
});

// 切换捕获模式
async function toggleCaptureMode() {
    const result = await chrome.storage.local.get(['nexusEnabled']);
    const newState = !result.nexusEnabled;
    
    await chrome.storage.local.set({ nexusEnabled: newState });
    
    chrome.notifications.create({
        type: 'basic',
        iconUrl: 'icons/icon48.png',
        title: 'NexusAI',
        message: newState ? '捕获模式已启用' : '捕获模式已禁用',
        priority: 1
    });
}

// 打开仪表板
function openDashboard() {
    chrome.tabs.create({
        url: chrome.runtime.getURL('dashboard.html')
    });
}

// 定期检查后端连接状态
setInterval(async () => {
    try {
        const result = await chrome.storage.local.get(['backendUrl']);
        const response = await fetch(`${result.backendUrl}/api/v1/health`);
        
        if (response.ok) {
            console.log('✅ 后端服务连接正常');
        } else {
            console.warn('⚠️ 后端服务连接异常');
        }
    } catch (error) {
        console.error('❌ 后端服务连接失败:', error);
    }
}, 30000); // 每30秒检查一次