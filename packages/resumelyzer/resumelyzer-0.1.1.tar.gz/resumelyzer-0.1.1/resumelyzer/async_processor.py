# async_processor.py
import asyncio
from typing import List
from .analyzer import analyze_personality
from .job_fit import match_resume_to_job

class RateLimiter:
    def __init__(self, max_calls: int, period: float):
        self.max_calls = max_calls
        self.period = period
        self.semaphore = asyncio.Semaphore(max_calls)
        
    async def call(self, coro):
        async with self.semaphore:
            await asyncio.sleep(self.period / self.max_calls)
            return await coro

# Free tier rate limiter (5 requests/minute)
free_rate_limiter = RateLimiter(5, 60)

async def analyze_bulk_personality(resumes: List[str], is_pro: bool = False) -> List[dict]:
    tasks = []
    for resume in resumes:
        if is_pro:
            task = analyze_personality(resume)
        else:
            task = free_rate_limiter.call(analyze_personality(resume))
        tasks.append(task)
    return await asyncio.gather(*tasks)