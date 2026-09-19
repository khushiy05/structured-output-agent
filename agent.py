import json
import logging
import os
from typing import Type, TypeVar

from anthropic import Anthropic
from pydantic import BaseModel, ValidationError
import ollama

MODEL = "llama3.2:1b"
T = TypeVar("T", bound=BaseModel)

logging.basicConfig(
    filename=os.path.join(os.path.dirname(__file__), "failures.log"),
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("structured_output_agent")


class StructuredOutputError(Exception):
    pass


def _build_prompt(schema, source_text, error_feedback=""):
    schema_json = json.dumps(schema.model_json_schema(), indent=2)
    feedback_block = ""
    if error_feedback:
        feedback_block = (
            f"\n\nYour previous attempt was INVALID. Fix this error:\n{error_feedback}\n"
        )

    example = """{
  "full_name": "Jane Doe",
  "email": "jane@example.com",
  "skills": ["Python", "SQL"],
  "experience": [
    {"company": "Acme", "title": "Engineer", "start_date": "2022", "end_date": "Present", "highlights": ["Did X"]}
  ],
  "education": [
    {"institution": "MIT", "degree": "B.S.", "field_of_study": "CS", "graduation_year": "2021"}
  ]
}"""

    return f"""You are a data extraction tool. Read the RESUME TEXT below and output
a JSON object containing the ACTUAL VALUES extracted from it.

Do NOT output the schema. Do NOT output field types or descriptions.
Output REAL DATA, like this example (this is just a formatting example,
not the real answer):

{example}

The fields you must fill in, with their types:
{schema_json}

Rules:
- Return ONLY the JSON object with real extracted values. No markdown fences, no commentary.
- If a field isn't present in the text, omit it or use null.
- Do not invent information that isn't in the source text.
{feedback_block}

RESUME TEXT:
---
{source_text}
---

JSON output (real values only):"""


def _extract_json(raw):
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())


def extract_structured(source_text, schema: Type[T], max_retries=3) -> T:
    error_feedback = ""
    last_raw_output = ""

    for attempt in range(1, max_retries + 1):
        prompt = _build_prompt(schema, source_text, error_feedback)
        response = ollama.chat(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        raw_output = response["message"]["content"]
        last_raw_output = raw_output

        try:
            parsed = _extract_json(raw_output)
            return schema.model_validate(parsed)
        except (json.JSONDecodeError, ValidationError) as e:
            error_feedback = str(e)
            logger.warning(f"Attempt {attempt} failed | {error_feedback[:300]}")

    logger.error(f"GAVE UP | last_raw_output={last_raw_output[:500]}")
    raise StructuredOutputError(f"Failed after {max_retries} attempts: {error_feedback}")