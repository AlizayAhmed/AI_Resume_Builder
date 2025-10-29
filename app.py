#streamlit entry point
import os
import streamlit as st
from io import BytesIO
from utils.resume_generator import generate_resume_structured
from utils.cover_letter import generate_cover_letter
from utils.interview_questions import generate_interview_questions
from utils.pdf_formatter import create_resume_pdf_bytes, create_cover_letter_pdf_bytes

# --- CONFIG ---
st.set_page_config(page_title="AI Resume Builder", layout="wide")

# --- HEADER ---
st.markdown(
    """
    <div style="display:flex;align-items:center;justify-content:space-between">
      <div>
        <h1 style="margin:0">AI Resume Builder</h1>
        <p style="margin:0;color:gray">Build Your Resume in Minutes — Powered by AI</p>
      </div>
      <div style="text-align:right;color:gray;font-size:13px">
        Powered by Groq LLM | Deployed on Streamlit Cloud
      </div>
    </div>
    <hr/>
    """,
    unsafe_allow_html=True,
)

# --- STATE ---
if "experiences" not in st.session_state:
    st.session_state.experiences = [
        {"role": "", "company": "", "duration": "", "description": ""}
    ]

def add_experience():
    st.session_state.experiences.append(
        {"role": "", "company": "", "duration": "", "description": ""}
    )

def remove_experience(idx):
    if len(st.session_state.experiences) > 1:
        st.session_state.experiences.pop(idx)

# --- EXPERIENCE MANAGEMENT BUTTONS ---
st.markdown("### Work Experience Entries")
exp_add_col1, exp_add_col2 = st.columns([1, 9])
if exp_add_col1.button("➕ Add Experience"):
    add_experience()
    st.experimental_rerun()

for i in range(len(st.session_state.experiences)):
    remove_col = st.columns([1, 9])[0]
    if remove_col.button(f"❌ Remove Experience #{i+1}", key=f"remove_{i}_outside"):
        remove_experience(i)
        st.experimental_rerun()

# --- FORM ---
with st.form("resume_form"):
    st.markdown("### Personal Information")
    col1, col2 = st.columns([2, 1])
    with col1:
        full_name = st.text_input("Full Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone (optional)")
    with col2:
        career_goal = st.text_input("Career Goal / Target Role")

    st.markdown("### Education")
    education = st.text_area(
        "Education Details (degree, institution, years, relevant coursework)",
        height=100,
    )

    st.markdown("### Work Experience Details")
    for i, exp in enumerate(st.session_state.experiences):
        st.markdown(f"**Experience #{i+1}**")
        cols = st.columns([2, 2, 1, 3])
        exp["role"] = cols[0].text_input(f"Role #{i+1}", exp["role"], key=f"role_{i}")
        exp["company"] = cols[1].text_input(f"Company #{i+1}", exp["company"], key=f"company_{i}")
        exp["duration"] = cols[2].text_input(f"Duration #{i+1}", exp["duration"], key=f"duration_{i}")
        exp["description"] = cols[3].textarea(
            f"Description #{i+1}", exp["description"], key=f"desc_{i}", height=80
        )

    st.markdown("### Skills & Additional Info")
    skills = st.text_area("Skills (comma-separated or newline)", height=80)
    additional_info = st.text_area("Additional Info / Achievements (optional)", height=80)

    # ✅ THIS IS THE PROPER SUBMIT BUTTON
    submitted = st.form_submit_button("🚀 Generate Resume")

# --- FOOTER ---
st.markdown("---")
st.markdown("⚠️ Generated content should be reviewed manually before submission.")

# --- SUBMIT HANDLER ---
if submitted:
    if not full_name or not email:
        st.error("Please provide at least Full Name and Email.")
    else:
        with st.spinner("Generating resume, cover letter, and interview questions..."):
            experiences_input = [
                e for e in st.session_state.experiences if any(v.strip() for v in e.values())
            ]
            applicant = {
                "full_name": full_name,
                "email": email,
                "phone": phone,
                "education": education,
                "experiences": experiences_input,
                "skills": skills,
                "career_goal": career_goal,
                "additional_info": additional_info,
            }

            resume_struct = generate_resume_structured(applicant)
            cover_letter_text = generate_cover_letter(applicant, resume_struct)
            interview_qs = generate_interview_questions(applicant)

        tabs = st.tabs(["Resume Preview", "Cover Letter", "Interview Questions"])

        # Resume
        with tabs[0]:
            st.subheader("Resume Preview")
            st.write(resume_struct)
            resume_text = []
            resume_text.append(f"# {resume_struct.get('name','')}\n")
            resume_text.append(f"**{resume_struct.get('title','')}**\n")
            if resume_struct.get("summary"):
                resume_text.append(f"**Summary**\n{resume_struct['summary']}\n")
            if resume_struct.get("experience"):
                resume_text.append("**Experience**")
                for ex in resume_struct["experience"]:
                    resume_text.append(
                        f"- **{ex.get('role','')}**, {ex.get('company','')} ({ex.get('duration','')})\n  - {ex.get('description','')}\n"
                    )
            if resume_struct.get("education"):
                resume_text.append("**Education**")
                for ed in resume_struct["education"]:
                    resume_text.append(
                        f"- {ed.get('degree','')} — {ed.get('institution','')} ({ed.get('years','')})"
                    )
            if resume_struct.get("skills"):
                resume_text.append("**Skills**")
                resume_text.append(", ".join(resume_struct["skills"]))
            if resume_struct.get("achievements"):
                resume_text.append("**Achievements**")
                for a in resume_struct["achievements"]:
                    resume_text.append(f"- {a}")

            pretty_resume_md = "\n\n".join(resume_text)
            st.markdown(pretty_resume_md)

            pdf_bytes = create_resume_pdf_bytes(resume_struct)
            st.download_button(
                "📄 Download Resume as PDF",
                data=pdf_bytes,
                file_name=f"{full_name.replace(' ', '_')}_Resume.pdf",
                mime="application/pdf",
            )

        # Cover Letter
        with tabs[1]:
            st.subheader("Cover Letter")
            st.markdown(cover_letter_text)
            cl_pdf = create_cover_letter_pdf_bytes(full_name, cover_letter_text)
            st.download_button(
                "📄 Download Cover Letter (PDF)",
                data=cl_pdf,
                file_name=f"{full_name.replace(' ', '_')}_CoverLetter.pdf",
                mime="application/pdf",
            )
            st.text_area("Copy Cover Letter Text", cover_letter_text, height=200)

        # Interview Questions
        with tabs[2]:
            st.subheader("Interview Questions")
            for i, q in enumerate(interview_qs, start=1):
                st.write(f"{i}. {q}")

        st.success("✅ Resume, Cover Letter, and Interview Questions Generated Successfully!")
