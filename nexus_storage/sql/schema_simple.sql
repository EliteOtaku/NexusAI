-- NexusAI 数据库架构定义（简化版）
-- 专为 RTX 4080 GPU 优化的存储结构

-- 会话表 (sessions)
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_uuid VARCHAR(36) UNIQUE NOT NULL,
    title VARCHAR(255) DEFAULT '未命名会话',
    description TEXT,
    platform VARCHAR(50) NOT NULL,
    platform_session_id VARCHAR(100),
    status VARCHAR(20) DEFAULT 'active',
    message_count INTEGER DEFAULT 0,
    token_count INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_active_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT
);

-- 消息表 (messages)
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    content_hash VARCHAR(64),
    platform_message_id VARCHAR(100),
    model_used VARCHAR(100),
    prompt_tokens INTEGER DEFAULT 0,
    completion_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    processing_time_ms INTEGER,
    response_latency_ms INTEGER,
    embedding_vector BLOB,
    embedding_model VARCHAR(100),
    embedding_dim INTEGER,
    summary TEXT,
    tags TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

-- 向量嵌入表 (vector_embeddings)
CREATE TABLE IF NOT EXISTS vector_embeddings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id INTEGER NOT NULL UNIQUE,
    embedding_data BLOB NOT NULL,
    embedding_model VARCHAR(100) NOT NULL,
    embedding_dim INTEGER NOT NULL,
    embedding_norm REAL,
    index_type VARCHAR(50) DEFAULT 'flat',
    index_params TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE CASCADE
);

-- 会话摘要表 (session_summaries)
CREATE TABLE IF NOT EXISTS session_summaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL UNIQUE,
    summary_text TEXT NOT NULL,
    summary_model VARCHAR(100),
    summary_prompt TEXT,
    coherence_score REAL,
    relevance_score REAL,
    summary_embedding BLOB,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

-- 搜索索引表 (search_index)
CREATE TABLE IF NOT EXISTS search_index (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id INTEGER NOT NULL,
    content_keywords TEXT,
    content_entities TEXT,
    topic_vector BLOB,
    sentiment_score REAL,
    indexed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE CASCADE
);

-- 会话表索引
CREATE INDEX IF NOT EXISTS idx_sessions_platform ON sessions(platform);
CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status);
CREATE INDEX IF NOT EXISTS idx_sessions_created ON sessions(created_at);
CREATE INDEX IF NOT EXISTS idx_sessions_updated ON sessions(updated_at);
CREATE INDEX IF NOT EXISTS idx_sessions_last_active ON sessions(last_active_at);
CREATE INDEX IF NOT EXISTS idx_sessions_uuid ON sessions(session_uuid);

-- 消息表索引
CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id);
CREATE INDEX IF NOT EXISTS idx_messages_role ON messages(role);
CREATE INDEX IF NOT EXISTS idx_messages_created ON messages(created_at);
CREATE INDEX IF NOT EXISTS idx_messages_platform ON messages(platform_message_id);
CREATE INDEX IF NOT EXISTS idx_messages_hash ON messages(content_hash);

-- 向量嵌入表索引
CREATE INDEX IF NOT EXISTS idx_vector_message ON vector_embeddings(message_id);
CREATE INDEX IF NOT EXISTS idx_vector_model ON vector_embeddings(embedding_model);

-- 会话摘要表索引
CREATE INDEX IF NOT EXISTS idx_summaries_session ON session_summaries(session_id);

-- 搜索索引表索引
CREATE INDEX IF NOT EXISTS idx_search_message ON search_index(message_id);

-- 插入示例数据
INSERT OR IGNORE INTO sessions (session_uuid, title, platform, description) VALUES
('550e8400-e29b-41d4-a716-446655440000', 'Python 编程学习', 'gemini', '关于 Python 基础语法的学习对话'),
('550e8400-e29b-41d4-a716-446655440001', '机器学习讨论', 'deepseek', '深度学习模型原理探讨'),
('550e8400-e29b-41d4-a716-446655440002', '项目架构设计', 'chatgpt', '软件系统架构设计讨论');

INSERT OR IGNORE INTO messages (session_id, role, content, model_used, total_tokens) VALUES
(1, 'user', '如何学习 Python 编程？', 'gemini-pro', 10),
(1, 'assistant', '建议从基础语法开始，然后学习数据结构和面向对象编程。', 'gemini-pro', 25),
(2, 'user', '什么是神经网络？', 'deepseek-coder', 8),
(2, 'assistant', '神经网络是模仿人脑神经元结构的机器学习模型。', 'deepseek-coder', 20);