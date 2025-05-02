# cache.py
import hashlib
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

CACHE_DIR = Path(".resumelyzer_cache")
CACHE_EXPIRY_DAYS = 30

def _get_cache_key(resume_text: str, analysis_type: str) -> str:
    """Generate a unique cache key for the resume content"""
    text_hash = hashlib.md5(resume_text.encode()).hexdigest()
    return f"{analysis_type}_{text_hash}"

def get_cached_result(resume_text: str, analysis_type: str):
    """Retrieve cached result if available"""
    CACHE_DIR.mkdir(exist_ok=True)
    cache_key = _get_cache_key(resume_text, analysis_type)
    cache_file = CACHE_DIR / f"{cache_key}.json"
    
    if cache_file.exists():
        with open(cache_file, 'r') as f:
            data = json.load(f)
            if datetime.now() < datetime.fromisoformat(data['expiry']):
                return data['result']
    return None

def store_result(resume_text: str, analysis_type: str, result: dict):
    """Store analysis result in cache"""
    CACHE_DIR.mkdir(exist_ok=True)
    cache_key = _get_cache_key(resume_text, analysis_type)
    cache_file = CACHE_DIR / f"{cache_key}.json"
    
    data = {
        'result': result,
        'expiry': (datetime.now() + timedelta(days=CACHE_EXPIRY_DAYS)).isoformat()
    }
    
    with open(cache_file, 'w') as f:
        json.dump(data, f)