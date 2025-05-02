import os
from openai import OpenAI
from dotenv import load_dotenv
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional

# Load API key from .env file
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Cache configuration
CACHE_DIR = Path(".resumelyzer_cache")
CACHE_EXPIRY_DAYS = 30

def _get_cache_key(resume_text: str, analysis_type: str) -> str:
    """Generate a unique cache key for the resume content"""
    text_hash = hashlib.md5(resume_text.encode()).hexdigest()
    return f"{analysis_type}_{text_hash}"

def _get_cached_result(cache_key: str) -> Optional[Dict]:
    """Retrieve cached result if available"""
    CACHE_DIR.mkdir(exist_ok=True)
    cache_file = CACHE_DIR / f"{cache_key}.json"
    
    if cache_file.exists():
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
                if datetime.now() < datetime.fromisoformat(data['expiry']):
                    return data['result']
        except (json.JSONDecodeError, KeyError):
            # Invalid cache file, remove it
            cache_file.unlink()
    return None

def _store_result(cache_key: str, result: Dict):
    """Store analysis result in cache"""
    CACHE_DIR.mkdir(exist_ok=True)
    cache_file = CACHE_DIR / f"{cache_key}.json"
    
    data = {
        'result': result,
        'expiry': (datetime.now() + timedelta(days=CACHE_EXPIRY_DAYS)).isoformat(),
        'generated_at': datetime.now().isoformat()
    }
    
    with open(cache_file, 'w') as f:
        json.dump(data, f)

def analyze_personality(resume_text: str, is_premium: bool = False) -> dict:
    """
    Analyze resume text and return personality traits.
    
    Args:
        resume_text: Text content of the resume
        is_premium: Whether to use premium (GPT-4) analysis
    
    Returns:
        Dictionary containing personality traits and soft skills
    """
    # Check cache first
    cache_key = _get_cache_key(resume_text, "personality_premium" if is_premium else "personality")
    cached = _get_cached_result(cache_key)
    if cached:
        return cached
    
    # Premium features get enhanced analysis
    model = "gpt-4" if is_premium else "gpt-3.5-turbo"
    prompt = f"""
    Analyze the following resume and predict the candidate's personality traits using the Big Five model.
    { "Provide detailed analysis with career suitability insights:" if is_premium else "" }
    
    Resume:
    \"\"\"
    {resume_text}
    \"\"\"

    Return the result as a JSON object like:
    {{
      "openness": float,
      "conscientiousness": float,
      "extroversion": float,
      "agreeableness": float,
      "neuroticism": float,
      "soft_skills": ["", ""],
      { '"career_suggestions": ["", "", ""],' if is_premium else '' }
      { '"communication_style": "",' if is_premium else '' }
      { '"ideal_work_environment": ""' if is_premium else '' }
    }}
    """

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            response_format={ "type": "json_object" }  # Ensure JSON output
        )

        content = response.choices[0].message.content
        result = json.loads(content)
        
        # Store result in cache
        _store_result(cache_key, result)
        return result
    
    except json.JSONDecodeError as e:
        print(f"Error parsing API response: {e}\nResponse content: {content}")
        return {
            "error": "Analysis failed - invalid response format",
            "details": str(e)
        }
    except Exception as e:
        print(f"Error analyzing personality: {e}")
        return {
            "error": "Analysis failed",
            "details": str(e)
        }

def bulk_analyze_personalities(resume_texts: list[str], is_premium: bool = False) -> list[dict]:
    """
    Analyze multiple resumes at once with optimized API calls
    
    Args:
        resume_texts: List of resume text contents
        is_premium: Whether to use premium analysis
    
    Returns:
        List of analysis results in the same order as input
    """
    # Implement basic version - in production you'd want to:
    # 1. Check cache for each resume first
    # 2. Batch uncached resumes together
    # 3. Use async API calls
    return [analyze_personality(text, is_premium) for text in resume_texts]