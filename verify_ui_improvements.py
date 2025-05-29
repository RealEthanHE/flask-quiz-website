#!/usr/bin/env python3
"""
UI对比度验证脚本
验证Quiz应用中所有文字对比度改进是否已正确实施
"""

import os
import re

def check_css_improvements():
    """检查CSS文件中的对比度改进"""
    css_file = 'd:/Project/XG/static/style.css'
    
    if not os.path.exists(css_file):
        print("❌ CSS文件不存在")
        return False
    
    with open(css_file, 'r', encoding='utf-8') as f:
        css_content = f.read()
    
    checks = [
        {
            'name': '选项文字颜色改进',
            'pattern': r'\.options label.*?color:\s*#1e293b',
            'description': '选项文字使用深色 #1e293b'
        },
        {
            'name': '选项背景对比度',
            'pattern': r'\.options div.*?background:.*rgba\(255,\s*255,\s*255,\s*0\.98\)',
            'description': '选项背景透明度提升到0.98'
        },
        {
            'name': '题目文字颜色',
            'pattern': r'\.question-text.*?color:\s*#1e293b',
            'description': '题目文字使用深色 #1e293b'
        },
        {
            'name': '容器背景对比度',
            'pattern': r'\.container-box.*?background:.*rgba\(255,\s*255,\s*255,\s*0\.99\)',
            'description': '主容器背景透明度提升到0.99'
        },
        {
            'name': '标题颜色改进',
            'pattern': r'h1.*?color:\s*#1e293b',
            'description': '标题使用深色 #1e293b'
        },
        {
            'name': '文字阴影增强',
            'pattern': r'text-shadow:\s*0\s+1px\s+2px\s+rgba\(255,\s*255,\s*255,\s*0\.8\)',
            'description': '添加白色文字阴影增强对比度'
        }
    ]
    
    results = []
    for check in checks:
        if re.search(check['pattern'], css_content, re.DOTALL | re.IGNORECASE):
            print(f"✅ {check['name']}: {check['description']}")
            results.append(True)
        else:
            print(f"❌ {check['name']}: 未找到预期的改进")
            results.append(False)
    
    return all(results)

def check_file_structure():
    """检查文件结构"""
    files_to_check = [
        'd:/Project/XG/static/style.css',
        'd:/Project/XG/templates/quiz_website.html',
        'd:/Project/XG/UI_CONTRAST_IMPROVEMENTS.md'
    ]
    
    all_exist = True
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ {os.path.basename(file_path)} 存在")
        else:
            print(f"❌ {os.path.basename(file_path)} 不存在")
            all_exist = False
    
    return all_exist

def main():
    print("🔍 Quiz应用UI对比度验证")
    print("=" * 50)
    
    print("\n📁 检查文件结构...")
    file_check = check_file_structure()
    
    print("\n🎨 检查CSS对比度改进...")
    css_check = check_css_improvements()
    
    print("\n" + "=" * 50)
    
    if file_check and css_check:
        print("🎉 所有UI对比度改进已成功实施！")
        print("\n主要改进:")
        print("• 选项文字使用深色 #1e293b，确保高对比度")
        print("• 选项背景透明度提升到0.98，增强可读性")
        print("• 题目文字采用深色，添加白色阴影增强对比")
        print("• 主容器背景透明度提升，保证内容清晰")
        print("• 所有标题和文本统一使用高对比度颜色")
        
        print("\n📋 用户操作建议:")
        print("1. 刷新浏览器页面以查看最新样式")
        print("2. 测试不同页面的文字可读性")
        print("3. 在移动设备上验证显示效果")
        
        return True
    else:
        print("❌ 部分改进未正确实施，请检查相关文件")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
