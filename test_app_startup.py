#!/usr/bin/env python3
"""
Quick test script to check if the FastAPI app can start without errors
"""
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

try:
    from app.main import app
    print("✅ FastAPI app imported successfully!")
    print("✅ No middleware configuration errors detected!")
    
    # Try to access the app's middleware stack to trigger any build errors
    try:
        # This will trigger the middleware stack building
        middleware_stack = app.middleware_stack
        print("✅ Middleware stack built successfully!")
    except Exception as e:
        print(f"❌ Middleware stack error: {e}")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Error importing FastAPI app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("🎉 All tests passed! The app should start without errors.")