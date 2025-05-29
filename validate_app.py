#!/usr/bin/env python3
"""
验证Flask应用程序的基本功能
"""
import sys
import os

def validate_app():
    """验证应用程序导入和基本功能"""
    try:
        print("🔍 正在验证应用程序...")
        
        # 检查是否能导入主要模块
        print("📦 导入database_manager...")
        from database_manager import db_manager
        print("✅ database_manager 导入成功")
        
        print("📦 导入main_new...")
        import main_new
        print("✅ main_new 导入成功")
        
        print("📊 检查问题数据...")
        question_count = len(main_new.ALL_QUESTION_DATA_PYTHON)
        print(f"✅ 问题总数: {question_count}")
          # 检查问题数据结构
        if question_count > 0:
            sample_question = main_new.ALL_QUESTION_DATA_PYTHON[0]
            required_keys = ['id', 'type', 'question', 'options', 'answer']  # Fixed: changed from 'correct_answer' to 'answer'
            for key in required_keys:
                if key not in sample_question:
                    print(f"❌ 问题数据缺少必需字段: {key}")
                    return False
            print("✅ 问题数据结构正确")
        
        print("🌐 检查Flask应用...")
        app = main_new.app
        print(f"✅ Flask应用创建成功: {app.name}")
          # 检查路由
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        expected_routes = ['/', '/login', '/register', '/quiz']
        for route in expected_routes:
            if route in routes:
                print(f"✅ 路由 {route} 存在")
            else:
                print(f"❌ 路由 {route} 缺失")
        
        print("\n🎉 应用程序验证完成!")
        return True
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False

if __name__ == '__main__':
    success = validate_app()
    sys.exit(0 if success else 1)
