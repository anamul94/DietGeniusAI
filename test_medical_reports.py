#!/usr/bin/env python3
"""
Simple test script to verify medical reports endpoints are working
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_medical_reports_endpoints():
    """Test that medical reports endpoints are accessible"""
    
    # Test that the endpoints are registered
    try:
        response = requests.get(f"{BASE_URL}/debug/routes")
        if response.status_code == 200:
            routes = response.json().get("routes", [])
            medical_routes = [r for r in routes if "medical-reports" in r.get("path", "")]
            
            print("Medical Reports Routes Found:")
            for route in medical_routes:
                print(f"  - {route['path']} [{', '.join(route.get('methods', []))}]")
                
            if medical_routes:
                print("✅ Medical reports endpoints are registered")
                return True
            else:
                print("❌ No medical reports endpoints found")
                return False
        else:
            print(f"❌ Could not fetch routes: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the server is running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error testing endpoints: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing Medical Reports API Endpoints...")
    test_medical_reports_endpoints()