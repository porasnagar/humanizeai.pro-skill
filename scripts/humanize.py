#!/usr/bin/env python3
"""
Convenience entry point for AI agents to run HumanizeAI Pro Swarm.
Usage:
  python scripts/humanize.py <input_file_or_text> [-o output] [-s style] [-f format] [-w workers]
"""

import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from humanizeai_pro.cli import main

if __name__ == "__main__":
    main()
