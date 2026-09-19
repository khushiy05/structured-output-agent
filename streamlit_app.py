import streamlit as st
import json

from agent import extract_structured, StructuredOutputError
from schemas import ResumeData
from formatter import render_resume

st.set_page_config(page_title="Structured Output Agent", page_icon="🧩", layout="wide")

st.title("🧩 Structured Output Agent")
st.caption("Paste resume text → get validated, structured JSON back, powered by a local LLM.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Input")
    resume_text = st.text_area(
        "Paste resume text here",
        height=400,
        placeholder="Paste a resume, or any messy text you want structured..."
    )
    run = st.button("Extract Structured Data", type="primary")

with col2:
    st.subheader("Output")

    if run:
        if not resume_text.strip():
            st.warning("Paste some text first.")
        else:
            with st.spinner("Extracting and validating..."):
                try:
                    result = extract_structured(resume_text, ResumeData, max_retries=3)
                    st.success("✅ Valid structured output")
                    st.json(result.model_dump())

                    st.subheader("📄 Formatted Resume")
                    formatted = render_resume(result)
                    st.text(formatted)
                except StructuredOutputError as e:
                    st.error(f"❌ Failed after retries: {e}")
                    st.caption("Check failures.log for full details of each failed attempt.")
    else:
        st.info("Output will appear here after you click Extract.")

with st.expander("How this works"):
    st.markdown("""
    1. Your text is sent to a local LLM (Ollama) with a strict schema it must follow.
    2. The response is validated against that schema using Pydantic.
    3. If validation fails, the exact error is fed back to the model and it retries — up to 3 times.
    4. Every failure is logged to `failures.log`, so nothing silently disappears.
    """)