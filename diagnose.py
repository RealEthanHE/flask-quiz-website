"""
简单的数据库问题诊断工具
"""
import sqlite3
import os
from werkzeug.security import generate_password_hash

def diagnose_database_issue():
    print("=== 数据库问题诊断 ===")
    
    # 检查本地数据库
    local_db = "database.db"
    print(f"1. 检查本地数据库: {local_db}")
    
    if os.path.exists(local_db):
        print("✅ 本地数据库文件存在")
        try:
            conn = sqlite3.connect(local_db)
            cursor = conn.cursor()
            
            # 检查表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"📋 表列表: {tables}")
            
            if ('users',) in tables:
                # 检查表结构
                cursor.execute("PRAGMA table_info(users)")
                columns = cursor.fetchall()
                print(f"🏗️ users表结构: {columns}")
                
                # 检查用户数量
                cursor.execute("SELECT COUNT(*) FROM users")
                count = cursor.fetchone()[0]
                print(f"👥 用户数量: {count}")
                
                # 尝试插入测试用户
                test_user = "debug_user"
                test_pass = generate_password_hash("debug_pass")
                
                try:
                    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                                 (test_user, test_pass))
                    conn.commit()
                    print("✅ 测试插入成功")
                    
                    # 验证插入
                    cursor.execute("SELECT * FROM users WHERE username = ?", (test_user,))
                    user = cursor.fetchone()
                    if user:
                        print(f"✅ 验证成功: 用户ID {user[0]}")
                    else:
                        print("❌ 验证失败: 未找到插入的用户")
                        
                except sqlite3.IntegrityError:
                    print("ℹ️ 用户已存在（这是正常的）")
                except Exception as e:
                    print(f"❌ 插入失败: {e}")
                    
            else:
                print("❌ users表不存在")
                
            conn.close()
            
        except Exception as e:
            print(f"❌ 数据库操作失败: {e}")
    else:
        print("❌ 本地数据库文件不存在")

def test_password_hashing():
    print("\n=== 密码哈希测试 ===")
    test_password = "testpass123"
    try:
        hashed = generate_password_hash(test_password)
        print(f"✅ 密码哈希成功: {hashed[:30]}...")
        
        from werkzeug.security import check_password_hash
        is_valid = check_password_hash(hashed, test_password)
        print(f"✅ 密码验证: {is_valid}")
        
    except Exception as e:
        print(f"❌ 密码哈希失败: {e}")

if __name__ == "__main__":
    diagnose_database_issue()
    test_password_hashing()
    print("\n=== 诊断完成 ===")
