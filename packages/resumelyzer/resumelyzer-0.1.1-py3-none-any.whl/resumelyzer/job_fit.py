import openai
import os
from dotenv import load_dotenv
import json

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def match_resume_to_job(resume_text: str, job_description: str) -> dict:
    prompt = f"""
Given the following resume and job description, evaluate how well the candidate fits the role.

Resume:
\"\"\"
{resume_text}
\"\"\"

Job Description:
\"\"\"
{job_description}
\"\"\"

Return a JSON with:
- fit_score (0.0 to 1.0),
- strengths (top 3 matching qualities),
- gaps (missing or weak areas),
- summary (short paragraph).

Use this JSON format:
{{
  "fit_score": float,
  "strengths": ["", "", ""],
  "gaps": ["", "", ""],
  "summary": ""
}}
    """

    response = openai.chat.completions.create(
        model="gpt-4",  # change to gpt-3.5-turbo if you prefer
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )

    try:
        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        print("Error parsing result:", e)
        return {}
