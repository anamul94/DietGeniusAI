#!/usr/bin/env python3
"""
Test script to verify Redis connection
"""
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.db.redis import check_redis_connection

if __name__ == "__main__":
    print("Testing Redis connection...")
    success = check_redis_connection()
    if success:
        print("✅ Redis connection successful!")
        sys.exit(0)
    else:
        print("❌ Redis connection failed!")
        sys.exit(1)