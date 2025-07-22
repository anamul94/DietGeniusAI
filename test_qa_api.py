#!/usr/bin/env python3
"""
API Test script for QA Summary endpoints
This script tests the QA summary API endpoints
"""

import requests
import json
from typing import Optional

class QASummaryAPITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        
    def set_auth_token(self, token: str):
        """Set authentication token for requests"""
        self.session.headers.update({
            'Authorization': f'Bearer {token}'
        })
    
    def test_get_latest_qa_summary(self) -> Optional[dict]:
        """Test GET /api/qa-summaries/latest"""
        try:
            response = self.session.get(f"{self.base_url}/api/qa-summaries/latest")
            print(f"GET /api/qa-summaries/latest - Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Response: {json.dumps(data, indent=2) if data else 'null'}")
                return data
            else:
                print(f"❌ Error: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            return None
    
    def test_get_all_qa_summaries(self, limit: int = 10) -> Optional[list]:
        """Test GET /api/qa-summaries/all"""
        try:
            params = {'limit': limit}
            response = self.session.get(f"{self.base_url}/api/qa-summaries/all", params=params)
            print(f"GET /api/qa-summaries/all?limit={limit} - Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Found {len(data)} summaries")
                for i, summary in enumerate(data, 1):
                    print(f"   {i}. Date: {summary['date']}")
                    print(f"      Summary: {summary['summary'][:80]}...")
                return data
            else:
                print(f"❌ Error: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            return None
    
    def test_get_user_qa_summary(self, user_id: int) -> Optional[dict]:
        """Test GET /api/qa-summaries/user/{user_id}/latest"""
        try:
            response = self.session.get(f"{self.base_url}/api/qa-summaries/user/{user_id}/latest")
            print(f"GET /api/qa-summaries/user/{user_id}/latest - Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Response: {json.dumps(data, indent=2) if data else 'null'}")
                return data
            else:
                print(f"❌ Error: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            return None

def print_api_documentation():
    """Print API documentation"""
    print("=== QA Summary API Documentation ===\n")
    
    print("Available Endpoints:")
    print("1. GET /api/qa-summaries/latest")
    print("   - Get the latest QA summary for authenticated user")
    print("   - Returns: {summary: string, date: string} or null")
    print()
    
    print("2. GET /api/qa-summaries/all?limit=10")
    print("   - Get all QA summaries for authenticated user")
    print("   - Query params: limit (1-50, default: 10)")
    print("   - Returns: [{summary: string, date: string}, ...]")
    print()
    
    print("3. GET /api/qa-summaries/user/{user_id}/latest")
    print("   - Get latest QA summary for specific user (admin access)")
    print("   - Returns: {summary: string, date: string} or null")
    print()

if __name__ == "__main__":
    print("QA Summary API Test")
    print("=" * 50)
    
    print_api_documentation()
    
    # Initialize tester
    tester = QASummaryAPITester("http://localhost:8000")
    
    # Note: You'll need to replace this with an actual JWT token
    # For testing, you can get a token from your auth endpoint
    sample_token = "your_jwt_token_here"
    
    if sample_token != "your_jwt_token_here":
        tester.set_auth_token(sample_token)
        
        print("=== Running API Tests ===\n")
        
        # Test 1: Get latest QA summary
        tester.test_get_latest_qa_summary()
        print()
        
        # Test 2: Get all QA summaries
        tester.test_get_all_qa_summaries(limit=5)
        print()
        
        # Test 3: Get user QA summary (if you have admin access)
        # tester.test_get_user_qa_summary(user_id=1)
        
    else:
        print("⚠️  Please replace 'your_jwt_token_here' with an actual JWT token")
        print("   You can get a token by calling your auth/login endpoint")
        print("\nExample usage:")
        print("   python test_qa_api.py")
        print("\nOr with curl:")
        print("   curl -H 'Authorization: Bearer YOUR_TOKEN' http://localhost:8000/api/qa-summaries/latest")