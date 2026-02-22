-- NexusAI 数据库架构定义
-- 专为 RTX 4080 GPU 优化的存储结构
-- 创建时间: $(date)

-- 注意：PRAGMA 语句必须在事务之外执行
-- 这些设置将在数据库连接时由 Python 脚本配置

-- 会话表 (sessions)
-- 存储用户与 AI 平台的对话会话
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- 会话基本信息
    session_uuid VARCHAR(36) UNIQUE NOT NULL,  -- 全局唯一标识符
    title VARCHAR(255) DEFAULT '未命名会话',   -- 会话标题（可自动生成）
    description TEXT,                          -- 会话描述
    
    -- 平台信息
    platform VARCHAR(50) NOT NULL,            -- AI 平台: gemini, deepseek, chatgpt, claude
    platform_session_id VARCHAR(100),         -- 平台端的会话ID
    
    -- 会话状态
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'archived', 'deleted')),
    
    -- 性能优化字段
    message_count INTEGER DEFAULT 0,           -- 消息数量（用于快速统计）
    token_count INTEGER DEFAULT 0,             -- 总 token 数（用于成本估算）
    
    -- 时间戳
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_active_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- 元数据（JSON格式，存储扩展信息）
    metadata JSON,
    
    -- 索引优化（为 GPU 加速查询设计）
    CONSTRAINT chk_platform CHECK (platform IN ('gemini', 'deepseek', 'chatgpt', 'claude', 'other'))
);

-- 消息表 (messages)
-- 存储会话中的具体对话消息
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- 关联会话
    session_id INTEGER NOT NULL,
    
    -- 消息内容
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),  -- 消息角色
    content TEXT NOT NULL,                      -- 消息内容
    content_hash VARCHAR(64),                   -- 内容哈希（用于去重）
    
    -- AI 平台相关信息
    platform_message_id VARCHAR(100),           -- 平台端的消息ID
    model_used VARCHAR(100),                    -- 使用的模型名称
    
    -- Token 统计（用于 GPU 优化）
    prompt_tokens INTEGER DEFAULT 0,            -- 输入 token 数
    completion_tokens INTEGER DEFAULT 0,         -- 输出 token 数
    total_tokens INTEGER DEFAULT 0,              -- 总 token 数
    
    -- 性能指标
    processing_time_ms INTEGER,                  -- 处理时间（毫秒）
    response_latency_ms INTEGER,                  -- 响应延迟
    
    -- 向量嵌入相关（GPU 加速）
    embedding_vector BLOB,                       -- 消息向量嵌入（二进制格式）
    embedding_model VARCHAR(100),                -- 使用的嵌入模型
    embedding_dim INTEGER,                       -- 向量维度
    
    -- 摘要和标签
    summary TEXT,                                -- 消息摘要（用于快速预览）
    tags JSON,                                   -- 标签系统（JSON数组）
    
    -- 时间戳
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- 元数据
    metadata JSON,
    
    -- 外键约束
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE,
    
    -- 索引优化（为 GPU 加速的语义搜索设计）
    CONSTRAINT chk_role CHECK (role IN ('user', 'assistant', 'system'))
);

-- 向量嵌入表 (vector_embeddings)
-- 专门存储消息的向量嵌入，优化 GPU 加速的语义搜索
CREATE TABLE IF NOT EXISTS vector_embeddings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- 关联消息
    message_id INTEGER NOT NULL UNIQUE,
    
    -- 嵌入信息
    embedding_data BLOB NOT NULL,               -- 向量数据（二进制格式）
    embedding_model VARCHAR(100) NOT NULL,      -- 嵌入模型名称
    embedding_dim INTEGER NOT NULL,             -- 向量维度
    embedding_norm REAL,                         -- 向量模长（用于相似度计算优化）
    
    -- 索引信息
    index_type VARCHAR(50) DEFAULT 'flat',      -- 索引类型: flat, ivf, hnsw
    index_params JSON,                          -- 索引参数
    
    -- 时间戳
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- 外键约束
    FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE CASCADE
);

-- 会话摘要表 (session_summaries)
-- 存储会话的自动生成摘要，优化上下文接力
CREATE TABLE IF NOT EXISTS session_summaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- 关联会话
    session_id INTEGER NOT NULL UNIQUE,
    
    -- 摘要内容
    summary_text TEXT NOT NULL,                 -- 摘要文本
    summary_model VARCHAR(100),                 -- 生成摘要的模型
    summary_prompt TEXT,                        -- 使用的提示词
    
    -- 质量评估
    coherence_score REAL,                        -- 连贯性评分（0-1）
    relevance_score REAL,                        -- 相关性评分（0-1）
    
    -- 向量嵌入（用于摘要的语义搜索）
    summary_embedding BLOB,
    
    -- 时间戳
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- 外键约束
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

-- 搜索索引表 (search_index)
-- 优化全文搜索和语义搜索性能
CREATE TABLE IF NOT EXISTS search_index (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- 关联消息
    message_id INTEGER NOT NULL,
    
    -- 搜索字段
    content_keywords TEXT,                       -- 关键词提取
    content_entities JSON,                       -- 命名实体识别
    
    -- 语义信息
    topic_vector BLOB,                           -- 主题向量
    sentiment_score REAL,                        -- 情感分析得分
    
    -- 时间戳
    indexed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- 外键约束
    FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE CASCADE
);

-- ==================== 触发器优化 ====================

-- 自动更新会话的更新时间戳
CREATE TRIGGER IF NOT EXISTS update_session_timestamp
AFTER UPDATE ON sessions
FOR EACH ROW
BEGIN
    UPDATE sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- 自动更新会话的最后活跃时间
CREATE TRIGGER IF NOT EXISTS update_session_last_active
AFTER INSERT ON messages
FOR EACH ROW
BEGIN
    UPDATE sessions SET last_active_at = CURRENT_TIMESTAMP, message_count = message_count + 1 
    WHERE id = NEW.session_id;
END;

-- 自动计算消息的 token 总数
CREATE TRIGGER IF NOT EXISTS calculate_message_tokens
BEFORE INSERT ON messages
FOR EACH ROW
WHEN NEW.prompt_tokens IS NOT NULL AND NEW.completion_tokens IS NOT NULL
BEGIN
    SET NEW.total_tokens = NEW.prompt_tokens + NEW.completion_tokens;
END;

-- 自动更新会话的 token 统计
CREATE TRIGGER IF NOT EXISTS update_session_token_count
AFTER INSERT ON messages
FOR EACH ROW
BEGIN
    UPDATE sessions SET token_count = token_count + NEW.total_tokens 
    WHERE id = NEW.session_id;
END;

-- ==================== 索引优化 ====================

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

-- ==================== 视图定义 ====================

-- 会话统计视图
CREATE VIEW IF NOT EXISTS session_stats AS
SELECT 
    s.id,
    s.session_uuid,
    s.title,
    s.platform,
    s.status,
    s.message_count,
    s.token_count,
    s.created_at,
    s.last_active_at,
    COUNT(m.id) as actual_message_count,
    SUM(m.total_tokens) as actual_token_count
FROM sessions s
LEFT JOIN messages m ON s.id = m.session_id
GROUP BY s.id, s.session_uuid, s.title, s.platform, s.status, s.message_count, s.token_count, s.created_at, s.last_active_at;

-- 平台使用统计视图
CREATE VIEW IF NOT EXISTS platform_usage AS
SELECT 
    platform,
    COUNT(*) as session_count,
    SUM(message_count) as total_messages,
    SUM(token_count) as total_tokens,
    AVG(message_count) as avg_messages_per_session
FROM sessions
WHERE status = 'active'
GROUP BY platform;

-- ==================== 初始化数据 ====================

-- 插入示例会话（用于测试）
INSERT OR IGNORE INTO sessions (session_uuid, title, platform, description) VALUES
('550e8400-e29b-41d4-a716-446655440000', 'Python 编程学习', 'gemini', '关于 Python 基础语法的学习对话'),
('550e8400-e29b-41d4-a716-446655440001', '机器学习讨论', 'deepseek', '深度学习模型原理探讨'),
('550e8400-e29b-41d4-a716-446655440002', '项目架构设计', 'chatgpt', '软件系统架构设计讨论');

-- 插入示例消息（用于测试）
INSERT OR IGNORE INTO messages (session_id, role, content, model_used, total_tokens) VALUES
(1, 'user', '如何学习 Python 编程？', 'gemini-pro', 10),
(1, 'assistant', '建议从基础语法开始，然后学习数据结构和面向对象编程。', 'gemini-pro', 25),
(2, 'user', '什么是神经网络？', 'deepseek-coder', 8),
(2, 'assistant', '神经网络是模仿人脑神经元结构的机器学习模型。', 'deepseek-coder', 20);

-- ==================== 数据库注释 ====================

COMMENT ON TABLE sessions IS '存储用户与 AI 平台的对话会话';
COMMENT ON TABLE messages IS '存储会话中的具体对话消息';
COMMENT ON TABLE vector_embeddings IS '存储消息的向量嵌入，优化 GPU 加速的语义搜索';
COMMENT ON TABLE session_summaries IS '存储会话的自动生成摘要，优化上下文接力';
COMMENT ON TABLE search_index IS '优化全文搜索和语义搜索性能';

COMMENT ON COLUMN sessions.session_uuid IS '全局唯一标识符，用于跨平台会话跟踪';
COMMENT ON COLUMN messages.embedding_vector IS '消息向量嵌入，用于 GPU 加速的语义相似度计算';
COMMENT ON COLUMN vector_embeddings.embedding_norm IS '向量模长，优化余弦相似度计算性能';

-- ==================== 性能优化提示 ====================

-- 定期运行 VACUUM 命令优化数据库性能
-- VACUUM;

-- 分析数据库性能统计
-- ANALYZE;

PRAGMA user_version = 1;  -- 数据库版本标记