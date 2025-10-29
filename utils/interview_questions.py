#Generate Interview_questions logic
import os
from groq import Groq

def _get_groq_client():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return None
    return Groq(api_key=api_key)

def _call_groq_for_qs(prompt):
    client = _get_groq_client()
    if not client:
        return None
    try:
        response = client.chat.completions.create(
            messages=[{"role":"user","content":prompt}],
            model="llama-3.3-70b-versatile",
        )
        return response.choices[0].message.content
    except Exception:
        return None

def _build_q_prompt(applicant, n=7):
    role = applicant.get("career_goal","")
    skills = applicant.get("skills","")
    prompt = f"""
Generate {n} interview questions tailored to the role: {role}.
Consider the applicant's skills: {skills}
Return a plain numbered or newline-separated list of questions only.
"""
    return prompt

def _fallback_local_questions(applicant, n=7):
    role = applicant.get("career_goal","") or "the target role"
    basic = [
        f"Tell me about yourself and why you're interested in {role}.",
        "Describe a challenging project you worked on — what was your role and what did you learn?",
        "Which tools or technologies are you most experienced with and how have you used them?",
        "How do you prioritize work when you have multiple deadlines?",
        "Describe a time you solved a technical or process problem. What approach did you take?",
        "How do you keep your skills up to date?",
        "Where do you see yourself in 2–3 years?"
    ]
    return basic[:n]

def generate_interview_questions(applicant, n=7):
    prompt = _build_q_prompt(applicant, n=n)
    res = _call_groq_for_qs(prompt)
    if res:
        # Split into lines and clean
        import re
        lines = [l.strip() for l in re.split(r'\n|\r', res) if l.strip()]
        # Try to remove leading numbering
        cleaned = [re.sub(r'^\d+[\).\s-]*','', l) for l in lines]
        return cleaned[:n] if cleaned else _fallback_local_questions(applicant, n=n)
    else:
        return _fallback_local_questions(applicant, n=n)
