import json
import logging
import os
from typing import Type, TypeVar

from pydantic import BaseModel, ValidationError
import ollama

MODEL = "llama3.2:latest"
T = TypeVar("T", bound=BaseModel)

logging.basicConfig(
    filename=os.path.join(os.path.dirname(__file__), "failures.log"),
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("structured_output_agent")


class StructuredOutputError(Exception):
    pass


# One formatting example per schema, keyed by the schema class name.
EXAMPLES = {
    "ResumeData": """{
  "full_name": "Jane Doe",
  "email": "jane@example.com",
  "skills": ["Python", "SQL"],
  "experience": [
    {"company": "Acme", "title": "Engineer", "start_date": "2022", "end_date": "Present", "highlights": ["Did X"]}
  ],
  "education": [
    {"institution": "MIT", "degree": "B.S.", "field_of_study": "CS", "graduation_year": "2021"}
  ]
}""",
    "ParagraphData": """{
  "summary": "A short neutral summary of the text.",
  "people": ["Person A"],
  "organizations": ["Company B"],
  "dates": ["1 March"],
  "amounts": ["$500"],
  "action_items": ["Do task X by Friday"],
  "key_points": ["Main point one"]
}""",
}

LABELS = {
    "ResumeData": "RESUME TEXT",
    "ParagraphData": "PARAGRAPH TEXT",
}


def _build_prompt(schema, source_text, error_feedback=""):
    schema_json = json.dumps(schema.model_json_schema(), indent=2)
    name = schema.__name__
    example = EXAMPLES.get(name, "{}")
    label = LABELS.get(name, "SOURCE TEXT")

    feedback_block = ""
    if error_feedback:
        feedback_block = (
            f"\n\nYour previous attempt was INVALID. Fix this error:\n{error_feedback}\n"
        )

    return f"""You are a data extraction tool. Read the {label} below and output
a JSON object containing the ACTUAL VALUES extracted from it.

Do NOT output the schema. Do NOT output field types or descriptions.
Output REAL DATA, formatted like this example. The example is ONLY for
formatting. NEVER copy any values from it:

{example}

The fields you must fill in, with their types:
{schema_json}

Rules:
- Return ONLY the JSON object with real extracted values. No markdown fences, no commentary.
- Only use information that appears in the {label}. Never invent or guess values.
- If a text field isn't present, use null. If a list field has nothing, use [].
- Fields typed as "array" in the schema MUST ALWAYS be JSON arrays (square brackets),
  even if there is only ONE item. Never output a single object where a list is expected.
{feedback_block}

{label}:
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