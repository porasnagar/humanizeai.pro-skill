#!/usr/bin/env python3
"""
Convenience entry point for running Critic fact and citation audits.
Usage:
  python scripts/critic.py --original <orig_file> --humanized <human_file>
"""

import argparse
import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from humanizeai_pro.critic import SemanticCritic
from humanizeai_pro.extractor import DocumentExtractor


def main():
    parser = argparse.ArgumentParser(description="Audit factual and citation fidelity.")
    parser.add_argument("--original", "-o", type=str, required=True, help="Original text or file path")
    parser.add_argument("--humanized", "-u", type=str, required=True, help="Humanized text or file path")
    args = parser.parse_args()

    orig_text = DocumentExtractor.extract(args.original)
    human_text = DocumentExtractor.extract(args.humanized)

    critic = SemanticCritic()
    audit = critic.audit(orig_text, human_text)

    print("=" * 60)
    print("CRITIC FACT & CITATION AUDIT REPORT")
    print("=" * 60)
    print(f"Status: {'PASSED' if audit.is_passed else 'WARNINGS DETECTED'}")
    print(f"Citations Found: {audit.total_citations_found} | Preserved: {len(audit.preserved_citations)} | Missing: {len(audit.missing_citations)}")
    print(f"Numbers/Stats Found: {audit.total_numbers_found} | Preserved: {len(audit.preserved_numbers)} | Missing: {len(audit.missing_numbers)}")
    if audit.notes:
        print("\nNotes / Discrepancies:")
        for n in audit.notes:
            print(f" - {n}")
    print("=" * 60)


if __name__ == "__main__":
    main()
