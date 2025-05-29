#!/usr/bin/env python3
"""
注册功能测试脚本
用于测试Flask应用的注册端点
"""
import requests
import json

# 测试URL - 请根据实际情况修改
BASE_URL = "https://flask-quiz-website.onrender.com"
# BASE_URL = "http://localhost:5000"  # 本地测试时使用

def test_register(username, password):
    """测试注册功能"""
    url = f"{BASE_URL}/register"
    data = {
        "username": username,
        "password": password
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"发送注册请求到: {url}")
    print(f"数据: {data}")
    
    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            json_response = response.json()
            print(f"JSON响应: {json_response}")
        
        return response.status_code == 201
        
    except Exception as e:
        print(f"请求失败: {e}")
        return False

def test_login(username, password):
    """测试登录功能"""
    url = f"{BASE_URL}/login"
    data = {
        "username": username,
        "password": password
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"\n发送登录请求到: {url}")
    print(f"数据: {data}")
    
    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"登录请求失败: {e}")
        return False

if __name__ == "__main__":
    print("=== Flask注册/登录功能测试 ===")
    
    # 测试用户信息
    test_username = "testuser123"
    test_password = "testpass123"
    
    print("1. 测试注册功能...")
    register_success = test_register(test_username, test_password)
    
    if register_success:
        print("\n2. 测试登录功能...")
        login_success = test_login(test_username, test_password)
        
        if login_success:
            print("\n✅ 注册和登录都成功！")
        else:
            print("\n❌ 注册成功但登录失败")
    else:
        print("\n❌ 注册失败")
    
    print("\n=== 测试完成 ===")
