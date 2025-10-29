# Resume generation logic
import os
from groq import Groq

def _get_groq_client():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return None
    return Groq(api_key=api_key)

def _call_groq(prompt):
    client = _get_groq_client()
    if not client:
        return None
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
        )
        return response.choices[0].message.content
    except Exception as e:
        # If Groq call fails, return None to trigger fallback
        return None

def _build_resume_prompt(applicant):
    # Build a prompt that asks for JSON-like structured output
    prompt = f"""
You are an assistant that produces a professional resume in JSON format for conversion to PDF.
Given the applicant info below, produce a JSON object with keys:
 - name (string)
 - title (string) - short professional title
 - summary (string)
 - experience (list of objects with role, company, duration, description)
 - education (list of objects with degree, institution, years)
 - skills (list of strings)
 - achievements (list of strings)

Applicant info:
Name: {applicant.get('full_name','')}
Email: {applicant.get('email','')}
Phone: {applicant.get('phone','')}
Career goal: {applicant.get('career_goal','')}
Education: {applicant.get('education','')}
Skills: {applicant.get('skills','')}
Additional info / achievements: {applicant.get('additional_info','')}
Work experiences:
"""
    for e in applicant.get("experiences", []):
        prompt += f"- Role: {e.get('role','')}, Company: {e.get('company','')}, Duration: {e.get('duration','')}, Description: {e.get('description','')}\n"

    prompt += """
Return only valid JSON. Keep descriptions concise (2-4 bullet-like sentences). For skills, split by commas or newlines into an array.
    """
    return prompt

def _fallback_local_generator(applicant):
    # Simple deterministic fallback generator if Groq key missing
    name = applicant.get("full_name","")
    title = applicant.get("career_goal","") or "Professional"
    summary = f"{name} is a {title} with experience in " + (", ".join([e.get("role","") for e in applicant.get("experiences",[]) if e.get("role")]) or "relevant areas") + "."
    experience = []
    for e in applicant.get("experiences", []):
        if any(v.strip() for v in e.values()):
            experience.append({
                "role": e.get("role",""),
                "company": e.get("company",""),
                "duration": e.get("duration",""),
                "description": e.get("description","")
            })
    # Parse skills
    skills_raw = applicant.get("skills","") or ""
    skills = [s.strip() for s in skills_raw.replace("\n",",").split(",") if s.strip()]
    education = []
    if applicant.get("education"):
        education.append({
            "degree": applicant.get("education"),
            "institution": "",
            "years": ""
        })
    achievements = [s.strip() for s in (applicant.get("additional_info","") or "").split("\n") if s.strip()]

    return {
        "name": name,
        "title": title,
        "summary": summary,
        "experience": experience,
        "education": education,
        "skills": skills,
        "achievements": achievements
    }

def generate_resume_structured(applicant):
    """
    Attempt to generate structured resume JSON via Groq. If API key missing or error occurs,
    return a fallback locally generated structure.
    """
    prompt = _build_resume_prompt(applicant)
    result = _call_groq(prompt)
    if result:
        # Attempt to parse JSON from model output. The model is asked to return only JSON.
        import json, re
        # Some models wrap json in ``` or explanations; extract the first { ... }
        m = re.search(r'(\{.*\})', result, re.S)
        json_text = m.group(1) if m else result
        try:
            parsed = json.loads(json_text)
            # Ensure keys exist
            return {
                "name": parsed.get("name",""),
                "title": parsed.get("title",""),
                "summary": parsed.get("summary",""),
                "experience": parsed.get("experience",[]),
                "education": parsed.get("education",[]),
                "skills": parsed.get("skills",[]),
                "achievements": parsed.get("achievements",[])
            }
        except Exception:
            # If parsing fails, fallback
            return _fallback_local_generator(applicant)
    else:
        return _fallback_local_generator(applicant)
