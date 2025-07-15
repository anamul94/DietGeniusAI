#!/usr/bin/env python3
"""
Simple test script to verify the meal types API endpoint
"""

import requests
import json
from typing import Dict, Any

def test_meal_types_endpoint(base_url: str = "http://localhost:8000") -> None:
    """
    Test the meal types API endpoint
    
    Args:
        base_url: Base URL of the API server
    """
    endpoint = f"{base_url}/api/v1/meal-entries/meal-types"
    
    try:
        print(f"Testing meal types endpoint: {endpoint}")
        
        # Make GET request to meal types endpoint
        response = requests.get(endpoint)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Success! Meal types retrieved:")
            print(json.dumps(data, indent=2))
            
            # Validate response structure
            if "meal_types" in data and "total_count" in data:
                print(f"\n📊 Total meal types available: {data['total_count']}")
                print("📋 Available meal types:")
                for meal_type in data["meal_types"]:
                    print(f"  - {meal_type['label']} ({meal_type['value']})")
            else:
                print("⚠️  Warning: Response structure doesn't match expected format")
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the API server is running")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request Error: {e}")
    except json.JSONDecodeError as e:
        print(f"❌ JSON Decode Error: {e}")
        print(f"Raw response: {response.text}")

def print_expected_meal_types() -> None:
    """Print the expected meal types from the enum"""
    print("\n🔍 Expected meal types based on MealType enum:")
    expected_types = [
        "breakfast", "lunch", "dinner", "snack", 
        "brunch", "supper", "other"
    ]
    
    for i, meal_type in enumerate(expected_types, 1):
        print(f"  {i}. {meal_type.title()} ({meal_type})")

if __name__ == "__main__":
    print("🧪 Testing Meal Types API Endpoint")
    print("=" * 50)
    
    # Print expected meal types first
    print_expected_meal_types()
    
    print("\n" + "=" * 50)
    
    # Test the endpoint
    test_meal_types_endpoint()
    
    print("\n" + "=" * 50)
    print("✨ Test completed!")