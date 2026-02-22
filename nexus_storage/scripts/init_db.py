#!/usr/bin/env python3
"""
NexusAI 数据库初始化脚本

功能：
1. 自动创建 SQLite 数据库
2. 执行 schema.sql 架构定义
3. 验证数据库完整性
4. 生成性能报告

专为 RTX 4080 GPU 优化的数据库配置
"""

import os
import sys
import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('nexus_storage/db_init.log')
    ]
)
logger = logging.getLogger('nexus_db_init')

class NexusDatabaseInitializer:
    """NexusAI 数据库初始化器"""
    
    def __init__(self, db_path: str = "nexus_storage/data/nexusai.db"):
        """
        初始化数据库初始化器
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = Path(db_path)
        self.schema_path = Path("nexus_storage/sql/schema_simple.sql")
        self.connection: Optional[sqlite3.Connection] = None
        
        # 创建数据目录
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
    def connect(self) -> bool:
        """连接到 SQLite 数据库"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            
            # 配置数据库性能优化
            self._configure_database()
            
            logger.info(f"[成功] 成功连接到数据库: {self.db_path}")
            return True
            
        except sqlite3.Error as e:
            logger.error(f"[错误] 数据库连接失败: {e}")
            return False
    
    def _configure_database(self) -> None:
        """配置数据库性能优化参数"""
        if not self.connection:
            return
            
        # 启用外键约束
        self.connection.execute("PRAGMA foreign_keys = ON")
        
        # 启用 WAL 模式（提升并发性能）
        self.connection.execute("PRAGMA journal_mode = WAL")
        
        # 优化同步设置
        self.connection.execute("PRAGMA synchronous = NORMAL")
        
        # 设置缓存大小（为 RTX 4080 优化）
        self.connection.execute("PRAGMA cache_size = -64000")  # 64MB 缓存
        
        # 设置页面大小
        self.connection.execute("PRAGMA page_size = 4096")
        
        logger.info("[配置] 数据库性能优化配置完成")
    
    def read_schema_file(self) -> Optional[str]:
        """读取 schema.sql 文件内容"""
        try:
            with open(self.schema_path, 'r', encoding='utf-8') as f:
                schema_content = f.read()
            
            logger.info(f"[读取] 成功读取架构文件: {self.schema_path}")
            return schema_content
            
        except FileNotFoundError:
            logger.error(f"[错误] 架构文件不存在: {self.schema_path}")
            return None
        except Exception as e:
            logger.error(f"[错误] 读取架构文件失败: {e}")
            return None
    
    def execute_schema(self, schema_content: str) -> bool:
        """执行数据库架构定义"""
        if not self.connection:
            logger.error("❌ 数据库连接未建立")
            return False
            
        try:
            # 分割 SQL 语句（支持多语句执行）
            sql_statements = self._split_sql_statements(schema_content)
            
            # 开始事务
            self.connection.execute("BEGIN TRANSACTION")
            
            # 执行所有 SQL 语句
            for i, statement in enumerate(sql_statements, 1):
                if statement.strip() and not statement.strip().startswith('--'):
                    try:
                        self.connection.execute(statement)
                        logger.debug(f"[执行] SQL 语句 {i}/{len(sql_statements)}")
                    except sqlite3.Error as e:
                        logger.error(f"[错误] SQL 语句执行失败 (语句 {i}): {e}")
                        logger.error(f"失败语句: {statement[:200]}...")
                        # 调试：打印所有语句
                        logger.error(f"所有语句列表:")
                        for j, s in enumerate(sql_statements, 1):
                            logger.error(f"语句 {j}: {s[:100]}...")
                        self.connection.rollback()
                        return False
            
            # 提交事务
            self.connection.commit()
            logger.info("[成功] 数据库架构创建成功")
            return True
            
        except Exception as e:
            logger.error(f"[错误] 执行架构定义失败: {e}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def _split_sql_statements(self, sql_content: str) -> list:
        """分割 SQL 语句（处理分号分隔的多语句）"""
        # 使用更智能的方法：按分号分割，但保留多行语句的完整性
        statements = []
        
        # 按行分割，然后重新组合
        lines = sql_content.split('\n')
        current_statement = ""
        
        for line in lines:
            line = line.strip()
            
            # 跳过空行和注释行
            if not line or line.startswith('--'):
                continue
                
            current_statement += ' ' + line
            
            # 如果行以分号结束，则完成当前语句
            if line.endswith(';'):
                statements.append(current_statement.strip())
                current_statement = ""
        
        # 添加最后一个语句（如果没有分号结尾）
        if current_statement.strip():
            statements.append(current_statement.strip() + ';')
        
        return statements
    
    def verify_database(self) -> Dict[str, Any]:
        """验证数据库完整性"""
        if not self.connection:
            return {"status": "error", "message": "数据库连接未建立"}
            
        try:
            verification_results = {
                "status": "success",
                "tables": {},
                "constraints": {},
                "performance": {}
            }
            
            # 检查表是否存在
            required_tables = ["sessions", "messages", "vector_embeddings", "session_summaries", "search_index"]
            
            cursor = self.connection.cursor()
            
            for table in required_tables:
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
                result = cursor.fetchone()
                verification_results["tables"][table] = bool(result)
            
            # 检查外键约束
            cursor.execute("PRAGMA foreign_key_list(messages)")
            fk_results = cursor.fetchall()
            verification_results["constraints"]["foreign_keys"] = len(fk_results) > 0
            
            # 检查索引
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='index'")
            index_count = cursor.fetchone()[0]
            verification_results["performance"]["index_count"] = index_count
            
            # 检查数据库大小
            db_size = self.db_path.stat().st_size if self.db_path.exists() else 0
            verification_results["performance"]["db_size_bytes"] = db_size
            verification_results["performance"]["db_size_mb"] = round(db_size / (1024 * 1024), 2)
            
            # 检查 WAL 模式
            cursor.execute("PRAGMA journal_mode")
            journal_mode = cursor.fetchone()[0]
            verification_results["performance"]["journal_mode"] = journal_mode
            
            cursor.close()
            
            logger.info("[验证] 数据库完整性验证完成")
            return verification_results
            
        except Exception as e:
            logger.error(f"[错误] 数据库验证失败: {e}")
            return {"status": "error", "message": str(e)}
    
    def generate_performance_report(self, verification_results: Dict[str, Any]) -> None:
        """生成性能报告"""
        logger.info("[报告] 生成数据库性能报告")
        
        print("\n" + "="*60)
        print("NexusAI 数据库性能报告")
        print("="*60)
        
        # 表状态
        print("\n表状态检查:")
        for table, exists in verification_results["tables"].items():
            status = "[存在]" if exists else "[缺失]"
            print(f"  {table}: {status}")
        
        # 约束状态
        print("\n约束检查:")
        fk_status = "[启用]" if verification_results["constraints"]["foreign_keys"] else "[禁用]"
        print(f"  外键约束: {fk_status}")
        
        # 性能指标
        print("\n性能指标:")
        print(f"  数据库大小: {verification_results['performance']['db_size_mb']} MB")
        print(f"  索引数量: {verification_results['performance']['index_count']}")
        print(f"  日志模式: {verification_results['performance']['journal_mode']}")
        
        # GPU 优化建议
        print("\nGPU 优化建议:")
        if verification_results["performance"]["db_size_mb"] > 100:
            print("  建议启用数据库分片策略")
        if verification_results["performance"]["index_count"] < 10:
            print("  建议为常用查询字段添加索引")
        
        print("\n" + "="*60)
    
    def backup_existing_database(self) -> bool:
        """备份现有数据库"""
        if not self.db_path.exists():
            logger.info("📁 数据库文件不存在，无需备份")
            return True
            
        try:
            backup_dir = Path("nexus_storage/backups")
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = backup_dir / f"nexusai_backup_{timestamp}.db"
            
            # 创建备份
            import shutil
            shutil.copy2(self.db_path, backup_path)
            
            logger.info(f"[备份] 数据库备份完成: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"[错误] 数据库备份失败: {e}")
            return False
    
    def initialize(self, backup: bool = True) -> bool:
        """执行完整的数据库初始化流程"""
        
        print("\n" + "="*60)
        print("NexusAI 数据库初始化工具")
        print("专为 RTX 4080 GPU 优化")
        print("="*60)
        
        # 步骤1: 备份现有数据库
        if backup and self.db_path.exists():
            print("\n1️⃣ 备份现有数据库...")
            if not self.backup_existing_database():
                response = input("备份失败，是否继续初始化？(y/N): ")
                if response.lower() != 'y':
                    return False
        
        # 步骤2: 连接数据库
        print("\n2️⃣ 连接数据库...")
        if not self.connect():
            return False
        
        # 步骤3: 读取架构文件
        print("\n3️⃣ 读取架构定义...")
        schema_content = self.read_schema_file()
        if not schema_content:
            return False
        
        # 步骤4: 执行架构定义
        print("\n4️⃣ 创建数据库架构...")
        if not self.execute_schema(schema_content):
            return False
        
        # 步骤5: 验证数据库
        print("\n5️⃣ 验证数据库完整性...")
        verification_results = self.verify_database()
        
        # 步骤6: 生成性能报告
        if verification_results["status"] == "success":
            self.generate_performance_report(verification_results)
        else:
            logger.error("❌ 数据库验证失败")
            return False
        
        # 步骤7: 关闭连接
        if self.connection:
            self.connection.close()
        
        print("\n[完成] 数据库初始化完成！")
        return True

def main():
    """主函数"""
    
    # 解析命令行参数
    import argparse
    parser = argparse.ArgumentParser(description='NexusAI 数据库初始化工具')
    parser.add_argument('--db-path', default='nexus_storage/data/nexusai.db', 
                       help='数据库文件路径')
    parser.add_argument('--no-backup', action='store_true',
                       help='跳过数据库备份')
    parser.add_argument('--schema-path', default='nexus_storage/sql/schema.sql',
                       help='架构文件路径')
    
    args = parser.parse_args()
    
    # 创建初始化器
    initializer = NexusDatabaseInitializer(args.db_path)
    
    # 执行初始化
    success = initializer.initialize(backup=not args.no_backup)
    
    if success:
        print("\n[成功] NexusAI 数据库已准备就绪！")
        print("下一步操作：")
        print("1. 启动后端服务: cd backend && python main.py")
        print("2. 访问 API 文档: http://localhost:8000/docs")
        print("3. 测试数据库连接")
        sys.exit(0)
    else:
        print("\n[失败] 数据库初始化失败")
        sys.exit(1)

if __name__ == "__main__":
    main()