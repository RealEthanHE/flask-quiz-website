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
from datetime import datetime
import json

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
            if self.is_postgres:  # PostgreSQL语法
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
                
                # 错题记录表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS wrong_answers (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id),
                        question_id VARCHAR(50) NOT NULL,
                        question_text TEXT NOT NULL,
                        question_type VARCHAR(20) NOT NULL,
                        correct_answer TEXT NOT NULL,
                        user_answer TEXT NOT NULL,
                        question_options JSON,
                        source_doc VARCHAR(50),
                        wrong_count INTEGER DEFAULT 1,
                        first_wrong_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_wrong_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_corrected BOOLEAN DEFAULT FALSE
                    )
                ''')
            else:                # SQLite语法
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
                
                # 错题记录表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS wrong_answers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        question_id TEXT NOT NULL,
                        question_text TEXT NOT NULL,
                        question_type TEXT NOT NULL,
                        correct_answer TEXT NOT NULL,
                        user_answer TEXT NOT NULL,
                        question_options TEXT,
                        source_doc TEXT,
                        wrong_count INTEGER DEFAULT 1,
                        first_wrong_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_wrong_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_corrected INTEGER DEFAULT 0,
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
    
    def add_wrong_answer(self, user_id, question_id, question_text, question_type, 
                        correct_answer, user_answer, question_options, source_doc):
        """添加错题记录"""
        # 检查是否已存在该错题
        if self.is_postgres:
            existing = self.execute_query(
                "SELECT id, wrong_count FROM wrong_answers WHERE user_id = %s AND question_id = %s",
                (user_id, question_id),
                fetch_one=True
            )
        else:
            existing = self.execute_query(
                "SELECT id, wrong_count FROM wrong_answers WHERE user_id = ? AND question_id = ?",
                (user_id, question_id),
                fetch_one=True
            )
        
        if existing:
            # 更新错题次数
            if self.is_postgres:
                query = "UPDATE wrong_answers SET wrong_count = wrong_count + 1, last_wrong_at = CURRENT_TIMESTAMP WHERE id = %s"
                params = (existing['id'],)
            else:
                query = "UPDATE wrong_answers SET wrong_count = wrong_count + 1, last_wrong_at = CURRENT_TIMESTAMP WHERE id = ?"
                params = (existing[0],)
            self.execute_query(query, params)
        else:
            # 添加新错题
            options_str = json.dumps(question_options) if question_options else None
            
            if self.is_postgres:
                query = '''INSERT INTO wrong_answers 
                          (user_id, question_id, question_text, question_type, correct_answer, 
                           user_answer, question_options, source_doc) 
                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'''
            else:                query = '''INSERT INTO wrong_answers 
                          (user_id, question_id, question_text, question_type, correct_answer, 
                           user_answer, question_options, source_doc) 
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''
            self.execute_query(query, (user_id, question_id, question_text, question_type, 
                                     correct_answer, user_answer, options_str, source_doc))
    
    def get_wrong_answers(self, user_id, limit=None):
        """获取用户的所有错题记录，按最后错误时间降序排列"""
        if self.is_postgres:
            query = '''SELECT id, user_id, question_id, question_text, question_type, 
                              correct_answer, user_answer, question_options, source_doc, 
                              wrong_count, last_wrong_at, is_corrected 
                       FROM wrong_answers 
                       WHERE user_id = %s 
                       ORDER BY last_wrong_at DESC'''
            params = (user_id,)
        else: # SQLite
            query = '''SELECT id, user_id, question_id, question_text, question_type, 
                              correct_answer, user_answer, question_options, source_doc, 
                              wrong_count, last_wrong_at, is_corrected 
                       FROM wrong_answers 
                       WHERE user_id = ? 
                       ORDER BY last_wrong_at DESC'''
            params = (user_id,)
        
        if limit:
            query += f" LIMIT {int(limit)}" # Ensure limit is an integer
        
        rows = self.execute_query(query, params, fetch_all=True)

        if not rows:
            return []

        processed_rows = []
        for row_obj in rows:
            # Convert sqlite3.Row to a mutable dictionary
            # For PostgreSQL, if execute_query already returns dicts, this is fine.
            # If it returns tuples, this conversion would need column names.
            # Assuming row_obj is dict-like (e.g., sqlite3.Row or dict from psycopg2)
            row_dict = dict(row_obj) 

            # Convert last_wrong_at string to datetime object
            if 'last_wrong_at' in row_dict and isinstance(row_dict['last_wrong_at'], str):
                try:
                    row_dict['last_wrong_at'] = datetime.strptime(row_dict['last_wrong_at'], '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    try:
                        # Attempt to parse with milliseconds if the first format fails
                        row_dict['last_wrong_at'] = datetime.strptime(row_dict['last_wrong_at'], '%Y-%m-%d %H:%M:%S.%f')
                    except ValueError:
                        # If parsing fails, set to None or log an error
                        logger.warning(f"Could not parse last_wrong_at timestamp: {row_dict['last_wrong_at']}")
                        row_dict['last_wrong_at'] = None 
            
            # Ensure is_corrected is boolean (for SQLite, it's 0 or 1)
            if not self.is_postgres and 'is_corrected' in row_dict:
                row_dict['is_corrected'] = bool(row_dict['is_corrected'])
            
            # Ensure question_options is a dict (it's stored as a JSON string)
            if 'question_options' in row_dict and isinstance(row_dict['question_options'], str):
                try:
                    row_dict['question_options'] = json.loads(row_dict['question_options'])
                except json.JSONDecodeError:
                    logger.warning(f"Could not parse question_options JSON: {row_dict['question_options']}")
                    row_dict['question_options'] = {} # Default to empty dict if parsing fails
            
            processed_rows.append(row_dict)
        
        return processed_rows
    
    def mark_question_corrected(self, user_id, question_id):
        """标记错题已纠正"""
        if self.is_postgres:
            query = "UPDATE wrong_answers SET is_corrected = TRUE WHERE user_id = %s AND question_id = %s"
        else:
            query = "UPDATE wrong_answers SET is_corrected = 1 WHERE user_id = ? AND question_id = ?"
        
        self.execute_query(query, (user_id, question_id))
    
    def get_wrong_answer_stats(self, user_id):
        """获取错题统计"""
        # 总错题数
        if self.is_postgres:
            total_query = "SELECT COUNT(*) as total FROM wrong_answers WHERE user_id = %s"
        else:
            total_query = "SELECT COUNT(*) as total FROM wrong_answers WHERE user_id = ?"
        total_result = self.execute_query(total_query, (user_id,), fetch_one=True)
        total_wrong = total_result['total'] if self.is_postgres else total_result[0]
        
        # 未纠正错题数
        if self.is_postgres:
            uncorrected_query = "SELECT COUNT(*) as uncorrected FROM wrong_answers WHERE user_id = %s AND is_corrected = %s"
            uncorrected_params = (user_id, False)
        else:
            uncorrected_query = "SELECT COUNT(*) as uncorrected FROM wrong_answers WHERE user_id = ? AND is_corrected = ?"
            uncorrected_params = (user_id, 0)
        uncorrected_result = self.execute_query(uncorrected_query, uncorrected_params, fetch_one=True)
        uncorrected_wrong = uncorrected_result['uncorrected'] if self.is_postgres else uncorrected_result[0]
        
        # 按题型统计
        if self.is_postgres:
            type_query = '''SELECT question_type, COUNT(*) as count 
                           FROM wrong_answers 
                           WHERE user_id = %s AND is_corrected = %s
                           GROUP BY question_type'''
            type_params = (user_id, False)
        else:
            type_query = '''SELECT question_type, COUNT(*) as count 
                           FROM wrong_answers 
                           WHERE user_id = ? AND is_corrected = ?
                           GROUP BY question_type'''
            type_params = (user_id, 0)
        type_results = self.execute_query(type_query, type_params, fetch_all=True)
        
        return {
            'total_wrong': total_wrong,
            'uncorrected_wrong': uncorrected_wrong,
            'by_type': type_results
        }

# 全局数据库管理器实例
db_manager = DatabaseManager()
