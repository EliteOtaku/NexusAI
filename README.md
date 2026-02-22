# 🛸 NexusAI: The Sovereign Bridge for AI Wasteland

"厂商修墙，我们挖洞。让数据主权回归个人。"

NexusAI 是一款专为 AI 重度用户设计的“个人逻辑枢纽”。它寄生于浏览器，利用本地算力（RTX 4080/128G RAM 优化），打破 Gemini、ChatGPT、DeepSeek 等各大 AI 平台之间的信息孤岛，实现无需 API、零成本、绝对隐私的上下文接力。

## 📸 项目愿景 (The Manifesto)

当各大 AI 厂商试图通过订阅费和闭源接口建立信息壁垒时， NexusAI 为个人开发者和研究者提供了一台“哔哔小子 (Pip-Boy)”。

- **无需 API**：通过浏览器插件直接抓取网页对话，省去高昂的 Token 费用。
- **本地记忆**：所有对话经由本地显卡（4080）进行向量化存储与逻辑蒸馏。
- **瞬间接力**：在不同 AI 窗口间一键同步上下文，让 DeepSeek 瞬间读懂你在 Gemini 里的奇思妙想。

## 🛠️ 核心模块 (Core Modules)

### 💾 1. The Vault (数据金库)
- **本地主权**：基于 SQLite 加密与 ChromaDB 向量索引，100% 本地运行。
- **语义搜索**：利用 128G 内存优势，毫秒级检索数万条历史对话，支持模糊逻辑匹配。

### 📡 2. Context Handover (上下文中继)
- **逻辑蒸馏**：利用本地运行的 deepseek-r1:7b 模型，自动将冗长对话浓缩为“接力提示词 (Bridge Prompt)”。
- **无缝注入**：模拟人工输入，一键将背景知识注入当前 AI 输入框。

## 🏗️ 技术架构与零门槛部署 (Architecture & Deployment)

NexusAI 追求“安装即用”，不再强制要求复杂的 Docker 环境。

| 组件 | 选用技术 | 部署方式 |
|------|----------|----------|
| 桌面客户端 | Electron | 一键安装 .exe 文件，集成所有 UI 逻辑。 |
| 推理引擎 | Ollama (Native) | 原生支持 Windows (.exe)。自动识别 CUDA，无需配置 Docker/WSL2。 |
| 数据核心 | SQLite + Vector DB | 内置于应用，无需用户手动配置数据库。 |
| 浏览器插件 | Manifest V3 | 实时监听网页 DOM，模拟人工操作，规避 API 限制。 |

## 🚀 快速启动 (For Everyone)

1. **下载安装包**：从 Release 页面获取 NexusAI_Setup.exe。
2. **环境预热**：
   - **小白用户**：直接安装 Ollama for Windows 原生版。NexusAI 将自动检测并拉取摘要模型。
   - **硬核用户**：如果你已有现成的 Docker/Ollama 环境，仅需在设置中指向对应的 API 地址。
3. **开始接力**：在任何 AI 网页端（Gemini/DeepSeek/ChatGPT）开启对话，右侧绿色的 Pip-Boy 标志将自动激活并开始记录。

## 🤝 贡献与公益 (Contribution)

本项起源于一个AI重度用户的深夜吐槽。

- **零门槛参与**：我们通过“语义化抓取”技术降低了维护难度，欢迎贡献新的网页解析器配置。
- **开源精神**：如果你厌倦了 API 账单和信息孤岛，欢迎加入我们。

## 📜 许可证 (License)

基于 MIT License 开源。
