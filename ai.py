from groq import Groq
import json
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def analyze_resume(resume_text, user_goal):
    prompt = f"""
    You are a senior software engineer, recruiter, ATS evaluator and hiring manager.

    Analyze the resume based on the user's target role.

    Target role:
    {user_goal}

    Resume:
    {resume_text}

    Instructions:

    1. Extract only skills relevant to the target role.
    2. Identify missing skills required for that role.
    3. Generate a learning roadmap to close the skill gap.
    4. Generate realistic interview questions.
    5. Estimate an ATS score from 0-100.
    6. Give practical suggestions to improve the resume.
    7. Ignore irrelevant skills.
    8. Return ONLY valid JSON.

    Return format:

    {{
        "ats_score": 0,
        "skills": [],
        "missing_skills": [],
        "roadmap": [],
        "interview_questions": [],
        "resume_suggestions": []
    }}
    """

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            messages=[
                {"role": "system", "content": "You're a strict hiring manager."},
                {"role":"user", "content":prompt}        
            ]
        ) 

        content = response.choices[0].message.content.strip()

        start = content.find("{")
        end = content.rfind("}")+1

        return json.loads(content[start:end])
    
    except Exception as e:
        return {
        "ats_score": 0,
        "skills": [],
        "missing_skills": [],
        "roadmap": [],
        "interview_questions": [],
        "resume_suggestions": [],
        "error": str(e)
        }
        