#cover letter fomration logic
import os
from groq import Groq

def _get_groq_client():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return None
    return Groq(api_key=api_key)

def _call_groq_for_cover(prompt):
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

def _build_cover_prompt(applicant, resume_struct):
    prompt = f"""
Write a professional, concise (approx 3-5 short paragraphs) cover letter addressed to "Hiring Manager".
Use the applicant info and resume structure below. Tailor the letter to the career goal: {applicant.get('career_goal','')}.
Include:
 - opening (what role they are applying to and a one-line summary why),
 - top 2-3 relevant experiences / strengths from resume,
 - enthusiasm & closing with contact info.

Applicant:
Name: {applicant.get('full_name','')}
Email: {applicant.get('email','')}
Phone: {applicant.get('phone','')}
Career Goal: {applicant.get('career_goal','')}

Resume summary: {resume_struct.get('summary','')}
Skills: {', '.join(resume_struct.get('skills',[]))}
Top experiences: 
"""
    for ex in resume_struct.get("experience", [])[:3]:
        prompt += f"- {ex.get('role','')} at {ex.get('company','')} ({ex.get('duration','')}): {ex.get('description','')}\n"

    prompt += "\nReturn only the cover letter text (no JSON)."
    return prompt

def _fallback_local_cover(applicant, resume_struct):
    name = applicant.get("full_name","")
    role = applicant.get("career_goal","") or "the role"
    summary = resume_struct.get("summary","")
    top_skills = ", ".join(resume_struct.get("skills",[])[:5])
    exp = resume_struct.get("experience",[])
    top_exp_line = ""
    if exp:
        first = exp[0]
        top_exp_line = f"In my role as {first.get('role','')} at {first.get('company','')}, I {first.get('description','')[:200]}."
    body = f"""Hiring Manager,

I am writing to express my interest in {role}. {summary}

{top_exp_line} I bring skills in {top_skills} and a consistent record of delivering results.

I would welcome the opportunity to discuss how my background aligns with your needs. You can reach me at {applicant.get('email','')}.

Sincerely,
{name}
"""
    return body

def generate_cover_letter(applicant, resume_struct):
    prompt = _build_cover_prompt(applicant, resume_struct)
    res = _call_groq_for_cover(prompt)
    if res:
        return res.strip()
    return _fallback_local_cover(applicant, resume_struct)
