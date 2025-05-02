# rate_limiter.py
from fastapi import HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# In your FastAPI route:
@router.post("/analyze")
@limiter.limit("5/minute")
async def analyze_resume(request: Request, resume_text: str):
    # Existing analysis logic