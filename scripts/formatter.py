#!/usr/bin/env python3
"""
Convenience entry point for compiling documents into MD, DOCX, PDF, or LaTeX.
Usage:
  python scripts/formatter.py <input_file> --format [md|docx|pdf|latex] -o <output_file>
"""

import argparse
import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from humanizeai_pro.extractor import DocumentExtractor
from humanizeai_pro.formatter import DocumentFormatter


def main():
    parser = argparse.ArgumentParser(description="Export document to various formats.")
    parser.add_argument("input", type=str, help="Input text or file path")
    parser.add_argument("-o", "--output", type=str, required=True, help="Destination output file path")
    parser.add_argument(
        "-f",
        "--format",
        type=str,
        default="md",
        choices=["md", "docx", "pdf", "latex", "tex"],
        help="Target output format",
    )
    args = parser.parse_args()

    text = DocumentExtractor.extract(args.input)
    saved_path = DocumentFormatter.export(text, args.output, format_type=args.format)
    print(f"Exported to: {saved_path}")


if __name__ == "__main__":
    main()
