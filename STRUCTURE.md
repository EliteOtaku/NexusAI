# 🏗️ NexusAI 项目目录结构定义

## 📋 项目概述

NexusAI 是一个专为 AI 重度用户设计的"个人逻辑枢纽"，通过本地算力（RTX 4080/128G RAM 优化）实现各大 AI 平台之间的上下文接力。

## 🎯 技术声明

**优先适配本地 NVIDIA GPU (RTX 4080) 加速**，充分利用本地算力实现：
- 向量嵌入生成（sentence-transformers + CUDA）
- 对话摘要推理（Ollama + CUDA）
- 语义搜索优化（ChromaDB + GPU）

## 📁 根目录结构

```
NexusAI/
├── nexus_core/          # Python 后端核心
├── nexus_extension/     # 浏览器插件
├── nexus_desktop/       # Electron 桌面应用
├── nexus_storage/       # 数据存储配置
├── scripts/            # 工具脚本
├── docs/              # 项目文档
└── tests/             # 集成测试
```

## 🔧 nexus_core/ - Python 后端核心

**核心功能**：FastAPI 后端服务、逻辑蒸馏 Prompt、本地模型调用接口

```
nexus_core/
├── app/                # FastAPI 应用主目录
│   ├── __init__.py
│   ├── main.py         # FastAPI 应用入口
│   ├── core/           # 核心配置
│   │   ├── config.py   # 应用配置管理
│   │   ├── database.py # 数据库连接池
│   │   └── security.py # 安全认证
│   ├── api/            # API 路由层
│   │   ├── v1/         # API v1 版本
│   │   │   ├── endpoints/
│   │   │   │   ├── conversations.py  # 对话管理
│   │   │   │   ├── search.py         # 语义搜索
│   │   │   │   ├── ollama.py         # Ollama 集成
│   │   │   │   └── plugin.py         # 插件通信
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── models/         # SQLAlchemy 数据模型
│   │   ├── conversation.py
│   │   ├── user.py
│   │   └── __init__.py
│   ├── schemas/        # Pydantic 模式定义
│   │   ├── conversation.py
│   │   └── __init__.py
│   ├── services/       # 业务逻辑服务
│   │   ├── embedding_service.py    # 向量嵌入服务
│   │   ├── vector_store.py         # 向量存储服务
│   │   ├── summary_service.py      # 对话摘要服务
│   │   └── __init__.py
│   ├── utils/          # 工具函数
│   │   ├── logger.py   # 日志配置
│   │   ├── prompts.py  # 逻辑蒸馏 Prompt
│   │   └── __init__.py
│   └── crud/           # 数据库 CRUD 操作
│       ├── conversation.py
│       └── __init__.py
├── requirements.txt    # Python 依赖
├── Dockerfile         # 容器化部署
└── README.md          # 后端说明文档
```

### 逻辑蒸馏 Prompt 设计 (`nexus_core/app/utils/prompts.py`)

```python
# 对话摘要蒸馏提示词
CONVERSATION_SUMMARY_PROMPT = """
请将以下对话内容浓缩成一段简明的摘要，保留核心逻辑和关键信息：

{conversation_text}

要求：
1. 保留技术细节和关键代码片段
2. 突出对话的逻辑流程
3. 控制在 100-200 字以内
4. 适合作为上下文接力使用
"""

# 语义搜索优化提示词
SEMANTIC_SEARCH_PROMPT = """
基于以下对话历史，生成最相关的搜索关键词：

{conversation_context}

当前查询：{user_query}

要求：
1. 提取核心概念和关键词
2. 考虑技术术语的精确性
3. 生成 3-5 个搜索关键词
"""
```

## 🌐 nexus_extension/ - 浏览器插件

**核心功能**：网页对话抓取、实时同步、UI 注入

```
nexus_extension/
├── manifest.json       # Chrome 插件清单
├── background.js       # 后台脚本
├── content/            # 内容脚本
│   ├── scraper.js      # 网页抓取逻辑
│   ├── injector.js     # UI 注入逻辑
│   └── dom_watcher.js  # DOM 变化监听
├── popup/              # 弹出窗口
│   ├── popup.html
│   ├── popup.js
│   └── popup.css
├── options/            # 设置页面
│   ├── options.html
│   ├── options.js
│   └── options.css
├── assets/             # 静态资源
│   ├── icons/          # 插件图标
│   │   ├── icon16.png
│   │   ├── icon48.png
│   │   └── icon128.png
│   └── styles/         # 样式文件
│       └── common.css
└── utils/              # 工具函数
    ├── api_client.js   # 后端 API 客户端
    ├── storage.js      # 本地存储管理
    └── logger.js       # 日志工具
```

### 抓取逻辑配置 (`nexus_extension/content/scraper.js`)

```javascript
// 支持的 AI 平台配置
const PLATFORM_CONFIGS = {
  'gemini': {
    selectors: {
      userMessage: '.user-message',
      aiResponse: '.ai-response',
      conversationContainer: '.conversation-container'
    },
    parser: 'parseGeminiConversation'
  },
  'deepseek': {
    selectors: {
      userMessage: '.user-input',
      aiResponse: '.ai-output',
      conversationContainer: '.chat-container'
    },
    parser: 'parseDeepSeekConversation'
  },
  'chatgpt': {
    selectors: {
      userMessage: '.user-msg',
      aiResponse: '.assistant-msg',
      conversationContainer: '.conversation'
    },
    parser: 'parseChatGPTConversation'
  }
};
```

## 💻 nexus_desktop/ - Electron 桌面应用

**核心功能**：窗口置顶、全局快捷键、悬浮球 UI

```
nexus_desktop/
├── src/                # 源代码目录
│   ├── main/           # 主进程代码
│   │   ├── main.js     # Electron 主进程
│   │   ├── window.js   # 窗口管理
│   │   ├── menu.js     # 菜单配置
│   │   └── shortcuts.js # 全局快捷键
│   ├── renderer/       # 渲染进程
│   │   ├── components/ # React 组件
│   │   │   ├── PipBoy/ # Pip-Boy 风格 UI
│   │   │   │   ├── PipBoy.jsx
│   │   │   │   ├── PipBoy.css
│   │   │   │   └── ScanLine.jsx
│   │   │   ├── Sidebar/ # 侧边栏
│   │   │   └── FloatingBall/ # 悬浮球
│   │   ├── pages/      # 页面组件
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Settings.jsx
│   │   │   └── History.jsx
│   │   ├── utils/      # 前端工具
│   │   │   ├── api.js  # API 调用
│   │   │   ├── storage.js
│   │   │   └── theme.js
│   │   └── App.jsx     # 主应用组件
│   └── shared/         # 共享代码
│       ├── constants.js
│       └── config.js
├── public/             # 静态资源
│   ├── index.html
│   ├── favicon.ico
│   └── assets/
├── package.json        # Node.js 依赖
├── electron-builder.json # 打包配置
└── webpack.config.js   # 构建配置
```

### 全局快捷键配置 (`nexus_desktop/src/main/shortcuts.js`)

```javascript
// 全局快捷键配置
const GLOBAL_SHORTCUTS = {
  'toggle-pipboy': {
    accelerator: 'CommandOrControl+Shift+P',
    action: 'togglePipBoy'
  },
  'quick-search': {
    accelerator: 'CommandOrControl+Shift+S',
    action: 'openQuickSearch'
  },
  'context-handover': {
    accelerator: 'CommandOrControl+Shift+C',
    action: 'triggerContextHandover'
  }
};
```

## 💾 nexus_storage/ - 数据存储配置

**核心功能**：数据库初始化、向量库配置、数据迁移

```
nexus_storage/
├── sql/                # SQL 初始化脚本
│   ├── init.sql        # 数据库初始化
│   ├── migrations/     # 数据迁移脚本
│   │   ├── 001_initial_schema.sql
│   │   ├── 002_add_vector_index.sql
│   │   └── 003_optimize_search.sql
│   └── seed_data.sql   # 初始数据
├── vector_db/          # 向量数据库配置
│   ├── chroma_config.yaml
│   ├── embedding_models/
│   │   ├── all-MiniLM-L6-v2/
│   │   └── custom-models/
│   └── collections/
│       ├── conversations.json
│       └── embeddings.json
├── backups/            # 数据备份
│   ├── auto_backup.sh
│   └── restore_tool.py
└── config/             # 存储配置
    ├── database.yaml   # 数据库配置
    ├── vector_store.yaml
    └── backup_policy.yaml
```

### 数据库初始化脚本 (`nexus_storage/sql/init.sql`)

```sql
-- NexusAI 数据库初始化脚本
-- 适配 RTX 4080 优化的存储结构

CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source VARCHAR(50) NOT NULL, -- gemini, deepseek, chatgpt
    user_message TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    metadata JSON,
    embedding_vector BLOB, -- 用于 GPU 加速的向量数据
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 为 GPU 优化创建索引
CREATE INDEX IF NOT EXISTS idx_conversations_source ON conversations(source);
CREATE INDEX IF NOT EXISTS idx_conversations_created ON conversations(created_at);

-- 向量搜索优化表
CREATE TABLE IF NOT EXISTS vector_embeddings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER,
    embedding_model VARCHAR(100),
    embedding_data BLOB,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);
```

## 🛠️ scripts/ - 工具脚本

**核心功能**：自动化部署、环境配置、性能测试

```
scripts/
├── deployment/         # 部署脚本
│   ├── deploy_local.sh # 本地部署
│   ├── deploy_docker.sh
│   └── setup_gpu.sh    # GPU 环境配置
├── development/        # 开发工具
│   ├── init_project.py # 项目初始化
│   ├── codegen/        # 代码生成器
│   │   ├── generate_model.py
│   │   └── generate_api.py
│   └── testing/        # 测试工具
│       ├── benchmark.py # 性能测试
│       └── load_test.py
├── automation/         # 自动化脚本
│   ├── backup_db.sh    # 数据库备份
│   ├── update_models.sh # 模型更新
│   └── cleanup_logs.sh
└── utils/              # 通用工具
    ├── env_setup.py    # 环境设置
    ├── dependency_check.py
    └── version_manager.py
```

### GPU 环境配置脚本 (`scripts/deployment/setup_gpu.sh`)

```bash
#!/bin/bash
# NexusAI GPU 环境配置脚本
# 专为 RTX 4080 优化

echo "🛸 配置 NexusAI GPU 加速环境"

# 检查 NVIDIA 驱动
if ! command -v nvidia-smi &> /dev/null; then
    echo "❌ NVIDIA 驱动未安装"
    exit 1
fi

# 检查 CUDA 版本
CUDA_VERSION=$(nvcc --version | grep release | awk '{print $5}')
echo "✅ 检测到 CUDA 版本: $CUDA_VERSION"

# 安装 GPU 加速的 Python 包
echo "📦 安装 GPU 加速依赖..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install chromadb[gpu]
pip install sentence-transformers[gpu]

# 配置 Ollama GPU 支持
echo "🤖 配置 Ollama GPU 支持..."
ollama serve --gpu

# 验证 GPU 加速
echo "🔍 验证 GPU 加速配置..."
python -c "import torch; print(f'GPU 可用: {torch.cuda.is_available()}'); print(f'GPU 设备: {torch.cuda.get_device_name(0)}')"

echo "✅ GPU 环境配置完成"
```

## 📊 技术架构特点

### 1. **GPU 优先设计**
- 向量计算：利用 RTX 4080 的 Tensor Cores 加速嵌入生成
- 模型推理：Ollama 本地模型 GPU 推理优化
- 内存管理：128G RAM 支持大规模对话缓存

### 2. **模块化架构**
- 前后端分离：Python 后端 + Electron 前端
- 插件化设计：支持多平台网页抓取
- 微服务思想：各模块独立部署

### 3. **本地主权保障**
- 数据本地化：SQLite + ChromaDB 本地存储
- 隐私保护：无需外部 API，零数据泄露风险
- 离线能力：核心功能完全离线运行

## 🚀 快速开始

### 环境要求
- **操作系统**: Windows 11 (优先适配)
- **GPU**: NVIDIA RTX 4080 (16GB VRAM)
- **内存**: 128GB RAM
- **Python**: 3.8+
- **Node.js**: 16+

### 部署步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/EliteOtaku/NexusAI.git
   cd NexusAI
   ```

2. **配置 GPU 环境**
   ```bash
   scripts/deployment/setup_gpu.sh
   ```

3. **初始化后端**
   ```bash
   cd nexus_core
   pip install -r requirements.txt
   python scripts/init_project.py
   ```

4. **启动桌面应用**
   ```bash
   cd nexus_desktop
   npm install
   npm run dev
   ```

5. **安装浏览器插件**
   - 打开 Chrome 扩展程序页面
   - 启用开发者模式
   - 加载 `nexus_extension` 目录

## 📝 维护说明

### 代码规范
- Python: PEP 8 + Black 格式化
- JavaScript: ESLint + Prettier
- Git: Conventional Commits

### 性能优化
- 定期运行 `scripts/development/testing/benchmark.py`
- 监控 GPU 使用率和内存占用
- 优化向量搜索算法

### 安全考虑
- 定期备份 `nexus_storage/backups/`
- 更新依赖包安全补丁
- 监控异常 API 调用

---

**📞 技术支持**: 如有问题，请参考各模块的 README 文档或提交 Issue。