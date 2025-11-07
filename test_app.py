#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for the Palestine News Web Application
"""

import requests
import json
import time

def test_web_app():
    """Test the web application endpoints"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Palestine News Web Application")
    print("=" * 50)
    
    try:
        # Test main page
        print("1. Testing main page...")
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            print("   ✅ Main page loads successfully")
        else:
            print(f"   ❌ Main page failed: {response.status_code}")
            return False
        
        # Test search page
        print("2. Testing search page...")
        response = requests.get(f"{base_url}/search", timeout=10)
        if response.status_code == 200:
            print("   ✅ Search page loads successfully")
        else:
            print(f"   ❌ Search page failed: {response.status_code}")
            return False
        
        # Test API endpoints
        print("3. Testing API endpoints...")
        
        # Test search API
        response = requests.get(f"{base_url}/api/search?q=غزة&per_page=5", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Search API works - found {data['total']} results")
        else:
            print(f"   ❌ Search API failed: {response.status_code}")
            return False
        
        # Test statistics API
        response = requests.get(f"{base_url}/api/statistics", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Statistics API works - {data['total_articles']} articles")
        else:
            print(f"   ❌ Statistics API failed: {response.status_code}")
            return False
        
        # Test timeline API
        response = requests.get(f"{base_url}/api/timeline", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Timeline API works - {len(data)} data points")
        else:
            print(f"   ❌ Timeline API failed: {response.status_code}")
            return False
        
        print("\n🎉 All tests passed! The web application is working correctly.")
        print(f"🌐 Visit: {base_url}")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the web application.")
        print("   Make sure the app is running: python app.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    # Wait a moment for the app to start
    print("⏳ Waiting for application to start...")
    time.sleep(3)
    
    success = test_web_app()
    
    if success:
        print("\n✅ Web application is ready to use!")
    else:
        print("\n❌ There are issues with the web application.")
        print("   Check the console output for error details.")
