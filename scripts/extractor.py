#!/usr/bin/env python3
"""
Convenience entry point for extracting text from TXT, MD, DOCX, PDF, and images.
Usage:
  python scripts/extractor.py <input_file> [-o output.txt]
"""

import argparse
import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from humanizeai_pro.extractor import DocumentExtractor


def main():
    parser = argparse.ArgumentParser(description="Extract clean text from documents.")
    parser.add_argument("input", type=str, help="Path to input document")
    parser.add_argument("-o", "--output", type=str, default=None, help="Output text file path")
    args = parser.parse_args()

    text = DocumentExtractor.extract(args.input)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"Extracted {len(text.split())} words to {args.output}")
    else:
        print(text)


if __name__ == "__main__":
    main()
