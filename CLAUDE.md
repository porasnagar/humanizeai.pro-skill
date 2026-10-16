# CLAUDE.md - HumanizeAI Pro Document Processor

## Project Overview
HumanizeAI Pro Swarm is an intelligent document processing and natural flow enhancement tool designed for long-form content. It coordinates sentence-boundary chunking, academic citation auditing, and multi-format compilation (Markdown, DOCX, PDF, LaTeX) with HumanizeAI.pro.

## Default Configuration
- **Writing Level**: `Difficult` (`advanced`) - Produces sophisticated, nuanced, and human-like sentence cadence.
- **Tone**: `Free` (`standard`) - Natural, balanced, and unconstrained tone.
- **Chunk Size**: `150-175 words` - Preserves complete context while retaining tables, code blocks, and markdown headers verbatim.

## Commands for Claude Code

### Humanize a Document
```bash
# Basic Humanization (Markdown)
python -m humanizeai_pro <input_file> -o <output_file>.md

# Academic Paper to Word (.docx)
python -m humanizeai_pro <input_file> -o <output_file>.docx -f docx

# Publication PDF
python -m humanizeai_pro <input_file> -o <output_file>.pdf -f pdf

# Academic LaTeX Document
python -m humanizeai_pro <input_file> -o <output_file>.tex -f latex
```

### Python API Integration
```python
from humanizeai_pro import HumanizerSwarm, SwarmConfig, DocumentExtractor, DocumentFormatter

raw_text = DocumentExtractor.extract("document.docx")
swarm = HumanizerSwarm(SwarmConfig(writing_level="advanced", style="standard"))
result = swarm.humanize(raw_text)

# Export
DocumentFormatter.export(result.humanized_text, "output.docx", format_type="docx")
```

### Run Tests
```bash
python tests/test_suite.py
```
