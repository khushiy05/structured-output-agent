import argparse
import json
import sys

from agent import extract_structured, StructuredOutputError
from schemas import ResumeData


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("--retries", type=int, default=3)
    args = parser.parse_args()

    if args.input == "-":
        source_text = sys.stdin.read()
    else:
        with open(args.input, "r", encoding="utf-8") as f:
            source_text = f.read()

    try:
        result = extract_structured(source_text, ResumeData, max_retries=args.retries)
    except StructuredOutputError as e:
        print(f"FAILED: {e}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result.model_dump(), indent=2))


if __name__ == "__main__":
    main()