import streamlit as st

from agent import extract_structured, StructuredOutputError
from schemas import ResumeData, ParagraphData
from formatter import render_resume

st.set_page_config(page_title="Structured Output Agent", page_icon="🧩", layout="wide")

st.title("🧩 Structured Output Agent")
st.caption("Paste text → get validated, structured JSON back, powered by a local LLM.")

mode = st.selectbox("Input type", ["Resume", "General paragraph"])
schema = ResumeData if mode == "Resume" else ParagraphData

col1, col2 = st.columns(2)

with col1:
    st.subheader("Input")
    input_text = st.text_area(
        f"Paste {mode.lower()} text here",
        height=400,
        placeholder="Paste your text here..."
    )
    run = st.button("Extract Structured Data", type="primary")

with col2:
    st.subheader("Output")

    if run:
        if not input_text.strip():
            st.warning("Paste some text first.")
        else:
            with st.spinner("Extracting and validating..."):
                try:
                    result = extract_structured(input_text, schema, max_retries=3)
                    st.success("✅ Valid structured output")
                    st.json(result.model_dump())

                    if mode == "Resume":
                        st.subheader("📄 Formatted Resume")
                        st.text(render_resume(result))
                    else:
                        st.subheader("📝 Summary")
                        st.write(result.summary)
                except StructuredOutputError as e:
                    st.error(f"❌ Failed after retries: {e}")
                    st.caption("Check failures.log for full details of each failed attempt.")
    else:
        st.info("Output will appear here after you click Extract.")

with st.expander("How this works"):
    st.markdown("""
    1. Pick an input type. Each type has its own Pydantic schema.
    2. Your text is sent to a local LLM (Ollama) with that schema.
    3. The response is validated against the schema using Pydantic.
    4. If validation fails, the exact error is fed back to the model and it retries, up to 3 times.
    5. Every failure is logged to `failures.log`.
    """)