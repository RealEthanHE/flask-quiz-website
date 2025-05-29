"""
数据库配置和连接管理
支持SQLite（开发环境）和PostgreSQL（生产环境）
"""
import os
import sqlite3
import psycopg2
import psycopg2.extras
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.database_url = os.environ.get('DATABASE_URL')
        self.is_postgres = self.database_url is not None
        
        if self.is_postgres:
            logger.info("使用PostgreSQL数据库")
            # 解析DATABASE_URL
            parsed = urlparse(self.database_url)
            self.db_config = {
                'host': parsed.hostname,
                'port': parsed.port,
                'database': parsed.path[1:],  # 移除开头的 '/'
                'user': parsed.username,
                'password': parsed.password
            }
        else:
            logger.info("使用SQLite数据库")
            self.sqlite_path = 'database.db'
    
    def get_connection(self):
        """获取数据库连接"""
        if self.is_postgres:
            conn = psycopg2.connect(**self.db_config)
            return conn
        else:
            conn = sqlite3.connect(self.sqlite_path)
            conn.row_factory = sqlite3.Row
            return conn
    
    def init_database(self):
        """初始化数据库表"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            if self.is_postgres:
                # PostgreSQL语法
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(255) NOT NULL UNIQUE,
                        password VARCHAR(255) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS quiz_results (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id),
                        score INTEGER,
                        total_questions INTEGER,
                        completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
            else:
                # SQLite语法
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS quiz_results (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        score INTEGER,
                        total_questions INTEGER,
                        completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                ''')
            
            conn.commit()
            logger.info("数据库表初始化成功")
            
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()
    
    def execute_query(self, query, params=None, fetch_one=False, fetch_all=False):
        """执行数据库查询的通用方法"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            if self.is_postgres:
                # PostgreSQL使用字典游标以便获取列名
                cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            cursor.execute(query, params or ())
            
            if fetch_one:
                result = cursor.fetchone()
            elif fetch_all:
                result = cursor.fetchall()
            else:
                result = None
            
            conn.commit()
            return result
            
        except Exception as e:
            conn.rollback()
            logger.error(f"数据库查询失败: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

# 全局数据库管理器实例
db_manager = DatabaseManager()
