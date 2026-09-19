# 🧩 Structured Output Agent

Paste resume text → get validated, structured JSON back, powered by a local LLM.

## What it does

This project takes messy, unstructured resume text and extracts it into a clean, validated, structured format using a local LLM (via Ollama). Instead of trusting the LLM to always return well-formed data, every response is validated against a strict schema — if it fails, the exact validation error is fed back to the model and it retries automatically, up to 3 times. Every failure is logged, so nothing silently disappears.

## Why

LLM output is unpredictable by default — it can hallucinate fields, return malformed JSON, or skip required data. That makes it unsafe to plug directly into downstream systems like a database, an ATS, or an API. This project solves that by enforcing a strict schema contract and building a self-correcting retry loop around the model, turning free-text LLM output into something a real system can actually rely on.

## Tech stack

- **Streamlit** – web UI
- **Pydantic** – schema definition and validation
- **Ollama** – local LLM inference
- **Python**

## How it works

1. User pastes resume text into the UI.
2. The text is sent to a local LLM with a strict schema (`ResumeData`) it must follow.
3. The response is validated against that schema using Pydantic.
4. If validation fails, the exact error is fed back to the model and it retries — up to 3 times.
5. Every failure is logged to `failures.log`.
6. On success, the structured data is rendered as both raw JSON and a clean, human-readable formatted resume.

## Project structure

```
structured-output-agent/
├── agent.py           # Calls the LLM, validates output, handles retries
├── schemas.py          # Pydantic schema (ResumeData) defining the data contract
├── formatter.py         # Renders validated data into readable resume text
├── streamlit_app.py      # Streamlit UI
├── requirements.txt
└── failures.log         # Logged validation failures
```

## Setup & run

```bash
pip install -r requirements.txt
python -m streamlit run streamlit_app.py
```

Make sure Ollama is installed and running locally with the required model pulled.

## Example output

Given a pasted resume, the app returns structured data including:

```json
{
  "full_name": "Khushi Yewale",
  "email": "khushi.yewale@email.com",
  "location": "Nagpur, Maharashtra, India",
  "skills": ["Python", "Flask", "Streamlit", "LLM"],
  "experience": [
    {
      "company": "NRSolution4U",
      "title": "AI/ML Intern",
      "start_date": "June 2026",
      "end_date": "Present",
      "highlights": ["Built and maintained an AI resume analyzer"]
    }
  ]
}
```

## Limitations & future work

- Currently resume-specific — the schema/pattern is reusable for other document types (invoices, forms, etc.) with a new Pydantic model.
- No persistence layer yet — extracted results aren't saved to a database.
- Local LLM accuracy may be lower than hosted models like GPT-4; retry logic helps compensate.
