from fastapi import HTTPException, Request, status
from typing import Dict
import time
from app.core.config import settings

class RateLimiter:
    def __init__(self):
        self.requests: Dict[str, list] = {}
    
    def is_allowed(self, key: str) -> bool:
        now = time.time()
        window_start = now - settings.RATE_LIMIT_WINDOW
        
        if key not in self.requests:
            self.requests[key] = []
        
        # Remove old requests
        self.requests[key] = [req_time for req_time in self.requests[key] if req_time > window_start]
        
        # Check if limit exceeded
        if len(self.requests[key]) >= settings.RATE_LIMIT_REQUESTS:
            return False
        
        # Add current request
        self.requests[key].append(now)
        return True

rate_limiter = RateLimiter()

def rate_limit_auth(request: Request):
    return None  # Disabled for now