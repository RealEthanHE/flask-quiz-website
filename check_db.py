import sqlite3

# 检查数据库
conn = sqlite3.connect('database.db')
cur = conn.cursor()

# 检查表
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cur.fetchall()
print("数据库中的表:", tables)

# 检查users表结构
if ('users',) in tables:
    cur.execute("PRAGMA table_info(users)")
    columns = cur.fetchall()
    print("users表结构:", columns)
    
    # 检查用户数量
    cur.execute("SELECT COUNT(*) FROM users")
    count = cur.fetchone()[0]
    print("用户数量:", count)
    
    # 显示所有用户
    if count > 0:
        cur.execute("SELECT * FROM users")
        users = cur.fetchall()
        print("所有用户:", users)
else:
    print("users表不存在!")

conn.close()
