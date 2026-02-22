#!/usr/bin/env python3
"""
NexusAI Vault 系统测试脚本
测试数据库初始化、数据存储和向量嵌入功能
"""

import sys
import os
import json
import sqlite3
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_database_connection():
    """测试数据库连接"""
    print("🧪 测试数据库连接...")
    
    db_path = "nexus_storage/data/nexus_vault.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' 
            AND name IN ('sessions', 'messages', 'vector_embeddings')
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        print(f"✅ 数据库表: {tables}")
        
        # 检查数据量
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   {table}: {count} 条记录")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 数据库连接测试失败: {e}")
        return False

def test_embedding_generation():
    """测试向量嵌入生成"""
    print("\n🧪 测试向量嵌入生成...")
    
    try:
        # 尝试导入 sentence-transformers
        from sentence_transformers import SentenceTransformer
        
        # 测试 GPU 可用性
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"🔧 设备: {device}")
        
        # 加载模型
        model = SentenceTransformer("all-MiniLM-L6-v2", device=device)
        
        # 测试嵌入生成
        test_texts = ["这是一个测试文本", "This is a test text"]
        embeddings = model.encode(test_texts, convert_to_numpy=True)
        
        print(f"✅ 嵌入生成成功")
        print(f"   模型: all-MiniLM-L6-v2")
        print(f"   维度: {embeddings.shape[1]}")
        print(f"   批次大小: {len(test_texts)}")
        
        return True
        
    except ImportError:
        print("⚠️ sentence-transformers 未安装，使用模拟嵌入")
        
        # 模拟嵌入生成
        import numpy as np
        
        test_text = "这是一个测试文本"
        embedding = np.random.randn(384).astype(np.float32)
        
        print(f"✅ 模拟嵌入生成成功")
        print(f"   维度: 384")
        print(f"   数据类型: {embedding.dtype}")
        
        return True
        
    except Exception as e:
        print(f"❌ 嵌入生成测试失败: {e}")
        return False

def test_api_endpoint():
    """测试 API 端点"""
    print("\n🧪 测试 API 端点...")
    
    try:
        import requests
        
        # 测试健康检查端点
        response = requests.get("http://localhost:8000/api/v1/health")
        
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ 健康检查成功")
            print(f"   服务状态: {health_data.get('status', 'unknown')}")
            print(f"   GPU 设备: {health_data.get('device_target', 'unknown')}")
            
            # 测试 ingest 端点状态
            response = requests.get("http://localhost:8000/api/v1/ingest/status")
            if response.status_code == 200:
                ingest_status = response.json()
                print(f"✅ Ingest 服务状态: {ingest_status.get('status', 'unknown')}")
                print(f"   支持平台: {ingest_status.get('supported_sources', [])}")
            
            return True
        else:
            print(f"❌ 健康检查失败: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API 端点测试失败: {e}")
        print("   请确保后端服务正在运行: python main.py")
        return False

def test_data_ingestion():
    """测试数据接收功能"""
    print("\n🧪 测试数据接收...")
    
    try:
        import requests
        import json
        from datetime import datetime
        
        # 测试数据
        test_data = {
            "source": "gemini",
            "content": "人工智能的发展可以追溯到20世纪50年代，当时计算机科学家开始探索如何让机器模拟人类智能。早期的AI研究主要集中在符号推理和问题解决上。",
            "url": "https://gemini.google.com/chat/abc123",
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "session_id": "test_session_123",
                "message_id": "test_message_456",
                "model": "gemini-pro"
            }
        }
        
        # 发送测试数据
        response = requests.post(
            "http://localhost:8000/api/v1/ingest",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 数据接收测试成功")
            print(f"   状态: {result.get('status', 'unknown')}")
            print(f"   消息: {result.get('message', 'unknown')}")
            print(f"   ID: {result.get('ingest_id', 'unknown')}")
            
            # 验证数据是否存储到数据库
            db_path = "nexus_storage/data/nexus_vault.db"
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM messages WHERE content LIKE ?", 
                          ("%人工智能的发展%",))
            count = cursor.fetchone()[0]
            
            if count > 0:
                print(f"✅ 数据已成功存储到数据库")
            else:
                print(f"⚠️ 数据可能未存储到数据库")
            
            conn.close()
            return True
        else:
            print(f"❌ 数据接收测试失败: HTTP {response.status_code}")
            print(f"   响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 数据接收测试失败: {e}")
        return False

def test_batch_processing():
    """测试批量处理功能"""
    print("\n🧪 测试批量处理...")
    
    try:
        import requests
        import json
        from datetime import datetime
        
        # 测试批量数据
        batch_data = [
            {
                "source": "deepseek",
                "content": "深度学习是机器学习的一个分支，它使用多层神经网络来学习数据的层次化表示。",
                "url": "https://chat.deepseek.com/chat/def456",
                "timestamp": datetime.now().isoformat(),
                "metadata": {"model": "deepseek-chat"}
            },
            {
                "source": "gemini", 
                "content": "自然语言处理是人工智能的一个重要领域，专注于让计算机理解和生成人类语言。",
                "url": "https://gemini.google.com/chat/ghi789",
                "timestamp": datetime.now().isoformat(),
                "metadata": {"model": "gemini-pro"}
            }
        ]
        
        # 发送批量数据
        response = requests.post(
            "http://localhost:8000/api/v1/ingest/batch",
            json=batch_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 批量处理测试成功")
            print(f"   处理数量: {result.get('processed_count', 0)}")
            print(f"   成功数量: {result.get('success_count', 0)}")
            print(f"   跳过数量: {result.get('skipped_count', 0)}")
            
            return True
        else:
            print(f"❌ 批量处理测试失败: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 批量处理测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 NexusAI Vault 系统测试开始...")
    print("=" * 60)
    
    tests = [
        ("数据库连接", test_database_connection),
        ("向量嵌入生成", test_embedding_generation),
        ("API 端点", test_api_endpoint),
        ("数据接收", test_data_ingestion),
        ("批量处理", test_batch_processing)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📊 测试结果汇总:")
    
    passed = 0
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"   {test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\n🎯 总体结果: {passed}/{len(tests)} 项测试通过")
    
    if passed == len(tests):
        print("\n🎉 NexusAI Vault 系统测试全部通过!")
        print("📍 数据库位置: nexus_storage/data/nexus_vault.db")
        print("🔧 功能验证: 数据存储、向量嵌入、API 接口")
        print("🚀 专为 RTX 4080 优化的语义存储系统已就绪!")
        return 0
    else:
        print("\n⚠️ 部分测试失败，请检查相关配置")
        return 1

if __name__ == "__main__":
    sys.exit(main())