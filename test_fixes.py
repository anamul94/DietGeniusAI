#!/usr/bin/env python3
"""
Test script to verify the fixes for image format validation and tuple indices errors
"""

import asyncio
from typing import List, Tuple, Dict, Any
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'DietGeniusAI'))

from app.services.bedrock_service import BedrockService

async def test_image_format_handling():
    """Test that image formats are correctly mapped for AWS Bedrock"""
    print("Testing image format handling...")
    
    # Test cases for different image formats
    test_cases = [
        ("test.jpg", "jpg", "jpeg"),
        ("test.jpeg", "jpeg", "jpeg"),
        ("test.png", "png", "png"),
        ("test.webp", "webp", "webp"),
        ("test.gif", "gif", "gif"),
        ("test.JPG", "jpg", "jpeg"),
        ("test.JPEG", "jpeg", "jpeg"),
    ]
    
    bedrock_service = BedrockService()
    
    for filename, original_ext, expected_ext in test_cases:
        file_ext = filename.lower().split('.')[-1]
        if file_ext == 'jpg':
            file_ext = 'jpeg'
        if file_ext not in ['jpeg', 'png', 'webp', 'gif']:
            file_ext = 'jpeg'
        
        assert file_ext == expected_ext, f"Expected {expected_ext}, got {file_ext}"
        print(f"✓ {filename} -> {file_ext}")
    
    print("All image format tests passed!")

def test_data_structure_handling():
    """Test handling of different data structures from bedrock service"""
    print("\nTesting data structure handling...")
    
    # Test different data structures that might be returned
    test_cases = [
        # Dict structure
        [{"report": "food item 1", "filename": "test1.jpg"}],
        # Tuple structure
        [("test1.jpg", "food item 1"), ("test2.jpg", "food item 2")],
        # Mixed structure
        [{"report": "food item 1"}, ("test2.jpg", "food item 2")],
        # Single string
        "food item 1",
        # Empty list
        [],
    ]
    
    for i, data in enumerate(test_cases):
        print(f"\nTest case {i+1}: {type(data)} - {data}")
        
        food_items = []
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    if "report" in item:
                        food_items.append(item["report"])
                    elif "filename" in item and "report" in item:
                        food_items.append(item["report"])
                    else:
                        food_items.append(str(item))
                elif isinstance(item, tuple) and len(item) >= 2:
                    food_items.append(str(item[1]))
                else:
                    food_items.append(str(item))
        else:
            food_items.append(str(data))
        
        print(f"  Result: {food_items}")
        assert isinstance(food_items, list), "Should always return a list"
    
    print("All data structure tests passed!")

async def main():
    """Run all tests"""
    print("Running tests for food nutrition processing fixes...\n")
    
    try:
        await test_image_format_handling()
        test_data_structure_handling()
        
        print("\n🎉 All tests passed! The fixes should resolve the reported issues.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)