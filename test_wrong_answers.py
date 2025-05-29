#!/usr/bin/env python3
"""
错题本功能测试脚本
用于测试错题本的各项功能
"""
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_manager import db_manager
import json

def test_wrong_answer_functionality():
    """测试错题本功能"""
    print("=== 错题本功能测试 ===\n")
    
    try:
        # 初始化数据库
        print("1. 初始化数据库...")
        db_manager.init_database()
        print("✅ 数据库初始化成功\n")
        
        # 创建测试用户（如果不存在）
        print("2. 创建测试用户...")
        test_user_id = 1  # 假设用户ID为1
        
        # 测试添加错题
        print("3. 测试添加错题...")
        test_question_data = {
            "question_id": "test_q1",
            "question_text": "测试题目：中国特色社会主义最本质的特征是什么？",
            "question_type": "single",
            "correct_answer": "C",
            "user_answer": "A",
            "question_options": {"A": "人民共同富裕", "B": "人民当家作主", "C": "中国共产党领导", "D": "社会主义现代化"},
            "source_doc": "导论.doc"
        }
        
        db_manager.add_wrong_answer(
            user_id=test_user_id,
            question_id=test_question_data["question_id"],
            question_text=test_question_data["question_text"],
            question_type=test_question_data["question_type"],
            correct_answer=test_question_data["correct_answer"],
            user_answer=test_question_data["user_answer"],
            question_options=test_question_data["question_options"],
            source_doc=test_question_data["source_doc"]
        )
        print("✅ 错题添加成功\n")
        
        # 测试获取错题列表
        print("4. 测试获取错题列表...")
        wrong_answers = db_manager.get_wrong_answers(test_user_id)
        print(f"✅ 获取到 {len(wrong_answers)} 道错题\n")
        
        # 显示错题详情
        if wrong_answers:
            print("5. 错题详情:")
            for i, wa in enumerate(wrong_answers, 1):
                if db_manager.is_postgres:
                    print(f"   {i}. 题目ID: {wa['question_id']}")
                    print(f"      题目: {wa['question_text'][:50]}...")
                    print(f"      错误次数: {wa['wrong_count']}")
                    print(f"      是否已纠正: {'是' if wa['is_corrected'] else '否'}")
                else:
                    print(f"   {i}. 题目ID: {wa[2]}")
                    print(f"      题目: {wa[3][:50]}...")
                    print(f"      错误次数: {wa[9]}")
                    print(f"      是否已纠正: {'是' if wa[11] else '否'}")
                print()
        
        # 测试获取错题统计
        print("6. 测试错题统计...")
        stats = db_manager.get_wrong_answer_stats(test_user_id)
        print(f"✅ 总错题数: {stats['total_wrong']}")
        print(f"✅ 未纠正错题数: {stats['uncorrected_wrong']}")
        print(f"✅ 按类型统计: {stats['by_type']}\n")
        
        # 测试标记纠正
        print("7. 测试标记错题为已纠正...")
        db_manager.mark_question_corrected(test_user_id, test_question_data["question_id"])
        print("✅ 标记纠正成功\n")
        
        # 再次检查统计
        print("8. 重新获取统计...")
        stats_after = db_manager.get_wrong_answer_stats(test_user_id)
        print(f"✅ 纠正后未纠正错题数: {stats_after['uncorrected_wrong']}")
        
        print("\n🎉 错题本功能测试完成！所有功能正常工作。")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_connection():
    """测试数据库连接"""
    print("=== 数据库连接测试 ===\n")
    
    try:
        # 测试连接
        conn = db_manager.get_connection()
        print(f"✅ 数据库连接成功")
        print(f"✅ 数据库类型: {'PostgreSQL' if db_manager.is_postgres else 'SQLite'}")
        
        # 测试简单查询
        cursor = conn.cursor()
        if db_manager.is_postgres:
            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0]
            print(f"✅ PostgreSQL版本: {version}")
        else:
            cursor.execute("SELECT sqlite_version()")
            version = cursor.fetchone()[0]
            print(f"✅ SQLite版本: {version}")
        
        cursor.close()
        conn.close()
        print("✅ 数据库连接测试完成\n")
        return True
        
    except Exception as e:
        print(f"❌ 数据库连接测试失败: {e}")
        return False

def clean_test_data():
    """清理测试数据"""
    print("=== 清理测试数据 ===\n")
    
    try:
        # 删除测试错题
        query = "DELETE FROM wrong_answers WHERE question_id = ?"
        params = ("test_q1",)
        db_manager.execute_query(query, params)
        print("✅ 测试数据清理完成\n")
        
    except Exception as e:
        print(f"❌ 清理测试数据失败: {e}")

if __name__ == "__main__":
    print("错题本功能完整测试\n")
    
    # 测试数据库连接
    if not test_database_connection():
        print("数据库连接失败，退出测试")
        sys.exit(1)
    
    # 测试错题本功能
    success = test_wrong_answer_functionality()
    
    # 清理测试数据
    clean_test_data()
    
    if success:
        print("✅ 所有测试通过！错题本功能可以正常使用。")
        sys.exit(0)
    else:
        print("❌ 测试失败！请检查错误信息。")
        sys.exit(1)
