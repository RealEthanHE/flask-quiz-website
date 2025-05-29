#!/usr/bin/env python3
# 数据库调试脚本
import sqlite3
import os

# 使用与main.py相同的数据库路径逻辑
if os.environ.get('RENDER') or os.environ.get('RAILWAY_ENVIRONMENT'):
    DATABASE = '/tmp/database.db'
else:
    DATABASE = 'database.db'

def check_database():
    print(f"检查数据库: {DATABASE}")
    print(f"数据库文件是否存在: {os.path.exists(DATABASE)}")
    
    if not os.path.exists(DATABASE):
        print("数据库文件不存在！")
        return False
    
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # 检查users表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        table_exists = cursor.fetchone() is not None
        print(f"users表是否存在: {table_exists}")
        
        if table_exists:
            # 检查表结构
            cursor.execute("PRAGMA table_info(users)")
            columns = cursor.fetchall()
            print("users表结构:")
            for col in columns:
                print(f"  {col}")
            
            # 检查现有用户
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            print(f"当前用户数量: {user_count}")
            
            if user_count > 0:
                cursor.execute("SELECT id, username FROM users LIMIT 5")
                users = cursor.fetchall()
                print("现有用户:")
                for user in users:
                    print(f"  ID: {user[0]}, 用户名: {user[1]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"数据库检查错误: {e}")
        return False

def test_insert():
    print("\n=== 测试插入新用户 ===")
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # 尝试插入测试用户
        test_username = "testuser_debug"
        test_password = "hashed_password_test"
        
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                      (test_username, test_password))
        conn.commit()
        print(f"成功插入测试用户: {test_username}")
        
        # 验证插入
        cursor.execute("SELECT * FROM users WHERE username = ?", (test_username,))
        user = cursor.fetchone()
        if user:
            print(f"验证成功: {user}")
        else:
            print("验证失败: 用户未找到")
            
        conn.close()
        
    except Exception as e:
        print(f"插入测试失败: {e}")

if __name__ == "__main__":
    print("=== 数据库调试工具 ===")
    if check_database():
        test_insert()
    else:
        print("数据库检查失败，无法进行测试")
