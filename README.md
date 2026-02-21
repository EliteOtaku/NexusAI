# 🛸 NexusAI: The Sovereign Bridge for AI Wasteland

**GitHub**: [https://github.com/EliteOtaku/NexusAI](https://github.com/EliteOtaku/NexusAI)

"厂商修墙，我们挖洞。让数据主权回归个人。"

NexusAI 是一款专为 AI 重度用户设计的"个人逻辑枢纽"。它寄生于浏览器，利用本地算力（RTX 4080/128G RAM 优化），打破 Gemini、ChatGPT、DeepSeek 等各大 AI 平台之间的信息孤岛，实现无需 API、零成本、绝对隐私的上下文接力。

## 📸 项目愿景 (The Manifesto)

当各大 AI 厂商试图通过订阅费和闭源接口建立信息壁垒时，NexusAI 为个人开发者和研究者提供了一台"哔哔小子 (Pip-Boy)"。

- **无需 API**：通过浏览器插件直接抓取网页对话，省去高昂的 Token 费用。
- **本地记忆**：所有对话经由本地显卡（4080）进行向量化存储与逻辑蒸馏。
- **瞬间接力**：在不同 AI 窗口间一键同步上下文，让 DeepSeek 瞬间读懂你在 Gemini 里的奇思妙想。

## 🛠️ 核心模块 (Core Modules)

### 💾 1. The Vault (数据金库)

- **本地主权**：基于 SQLite 加密与 ChromaDB 向量索引，100% 本地运行。
- **语义搜索**：利用 128G 内存优势，毫秒级检索数万条历史对话，支持模糊逻辑匹配。

### 📡 2. Context Handover (上下文中继)

- **逻辑蒸馏**：利用本地运行的 deepseek-r1:7b 模型，自动将冗长对话浓缩为"接力提示词 (Bridge Prompt)"。
- **无缝注入**：模拟人工输入，一键将背景知识注入当前 AI 输入框。

### 🟢 3. Pip-Boy UI (极客交互)

- **复古终端**：借鉴《辐射》风格的绿色扫描线界面，作为 VScode 侧边栏或桌面悬浮窗存在。
- **HUD 监控**：实时显示当前本地显存 (VRAM) 占用与逻辑识别状态。

## 🏗️ 技术架构 (Technical Stack)

| 组件 | 选用技术 | 理由 |
|------|----------|------|
| 桌面客户端 | Electron + React | 跨平台兼容，支持 Windows 11 置顶窗口。 |
| 逻辑后端 | FastAPI (Python) | 与 RTX 4080 通讯的母语，性能澎湃。 |
| 浏览器插件 | Manifest V3 | 实时监听网页 DOM，模拟人工操作，规避 API 限制。 |
| 本地推理 | Ollama / PyTorch | 充分利用 4080 显存，实现全离线摘要生成。 |

## 🚀 快速启动 (For High-End Rig Users)

**硬件要求**：建议 RTX 3080/4080 (16G VRAM) + 64G/128G RAM。

1. **下载安装包**：从 Release 页面获取 NexusAI_Setup.exe。
2. **安装插件**：按照指引在 Chrome/Edge 扩展商店添加 NexusAI 助手。
3. **点亮算力**：开启本地 Ollama 服务，NexusAI 将自动识别你的 4080 显卡并进行预热。
4. **开始接力**：在任何 AI 网页端开启对话，你会看到右侧绿色的 Pip-Boy 标志已激活。

## 🤝 贡献与公益 (Contribution)

本项起源于一个 2280 分 GRE 逻辑怪的深夜吐槽。我们不打算靠这个赚钱，我们只想要自由地管理我们的 AI 资产。

- **代码能力不限**：欢迎贡献网页解析器（Selector）配置、UI 皮肤或者你的逻辑调教心得。
- **署名权**：所有贡献者都将永久保留在 Credits 列表中。

## 📜 许可证 (License)

基于 MIT License 开源。
