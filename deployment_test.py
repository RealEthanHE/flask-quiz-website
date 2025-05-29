#!/usr/bin/env python3
"""
Quick deployment verification script
Run this after deployment to verify the application is working correctly
"""

import requests
import sys
from urllib.parse import urljoin

def test_deployment(base_url):
    """Test the deployed application endpoints"""
    print(f"🌐 Testing deployment at: {base_url}")
    
    try:
        # Test home page
        print("📍 Testing home page...")
        response = requests.get(base_url, timeout=10)
        if response.status_code == 200:
            print("✅ Home page accessible")
        else:
            print(f"❌ Home page failed: {response.status_code}")
            return False
        
        # Test login page
        print("📍 Testing login page...")
        login_url = urljoin(base_url, '/login')
        response = requests.get(login_url, timeout=10)
        if response.status_code == 200:
            print("✅ Login page accessible")
        else:
            print(f"❌ Login page failed: {response.status_code}")
            return False
        
        # Test register page
        print("📍 Testing register page...")
        register_url = urljoin(base_url, '/register')
        response = requests.get(register_url, timeout=10)
        if response.status_code == 200:
            print("✅ Register page accessible")
        else:
            print(f"❌ Register page failed: {response.status_code}")
            return False
        
        print("\n🎉 All basic endpoints are working!")
        print("✨ Your Flask quiz application is successfully deployed!")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python deployment_test.py <your-render-url>")
        print("Example: python deployment_test.py https://your-app.onrender.com")
        sys.exit(1)
    
    url = sys.argv[1]
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    success = test_deployment(url)
    sys.exit(0 if success else 1)
