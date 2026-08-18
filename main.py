"""
Resume Parser - Main Entry Point

A tool to parse resumes (PDF, DOCX, TXT) and extract structured information
using both regex-based and LLM-based parsing approaches.
"""

import argparse
import json
import sys
from pathlib import Path

from utils import read_file_content, clean_text, logger
from regex_parser import parse_resume as regex_parse
from llm_parser import parse_resume_with_llm



def main():
    parser = argparse.ArgumentParser(
        description="Parse resumes and extract structured information.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s resume.pdf
  %(prog)s resume.pdf --method llm --api-key sk-xxx
  %(prog)s resume.docx --output result.json
  %(prog)s resume.txt --method regex --pretty
        """,
    )

    parser.add_argument(
        "file",
        type=str,
        help="Path to the resume file (PDF, DOCX, or TXT)",
    )
    parser.add_argument(
        "--method",
        "-m",
        type=str,
        choices=["regex", "llm", "both"],
        default="regex",
        help="Parsing method to use (default: regex)",
    )
    parser.add_argument(
        "--api-key",
        type=str,
        help="Groq API key (required for LLM method)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="llama-3.3-70b-versatile",
        help="LLM model to use (default: gpt-3.5-turbo)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Output file path (prints to stdout if not specified)",
    )
    parser.add_argument(
        "--pretty",
        "-p",
        action="store_true",
        help="Pretty-print JSON output",
    )

    args = parser.parse_args()

    # Validate file exists
    file_path = Path(args.file)
    if not file_path.exists():
        logger.error(f"File not found: {args.file}")
        sys.exit(1)

    # Read the file
    try:
        logger.info(f"Reading file: {args.file}")
        raw_text = read_file_content(str(file_path))
        cleaned_text = clean_text(raw_text)
        logger.info(f"Extracted {len(cleaned_text)} characters of text")
    except Exception as e:
        logger.error(f"Failed to read file: {e}")
        sys.exit(1)

    # Parse the resume
    result = {}

    if args.method in ("regex", "both"):
        logger.info("Parsing with regex...")
        result["regex"] = regex_parse(cleaned_text)
        logger.info("Regex parsing complete")

    if args.method in ("llm", "both"):
        if not args.api_key:
            logger.error("API key is required for LLM parsing. Use --api-key or set OPENAI_API_KEY env var.")
            sys.exit(1)

        logger.info(f"Parsing with LLM ({args.model})...")
        try:
            result["llm"] = parse_resume_with_llm(
                cleaned_text,
                api_key=args.api_key,
                model=args.model,
            )
            logger.info("LLM parsing complete")
        except Exception as e:
            logger.error(f"LLM parsing failed: {e}")
            sys.exit(1)

    # If only one method, flatten the result
    if args.method != "both" and result:
        result = result[args.method]

    # Output the result
    output = json.dumps(result, indent=2 if args.pretty else None, default=str)

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(output, encoding="utf-8")
        logger.info(f"Results saved to: {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
