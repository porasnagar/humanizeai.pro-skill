# HumanizeAI Pro Multi-Agent Swarm

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8%2B-brightgreen.svg)](https://python.org)
[![Agents: Claude Code | Antigravity | Codex | Hermes](https://img.shields.io/badge/Agents-Universal_Skill-purple.svg)]()
[![Writing Level: Very difficult](https://img.shields.io/badge/Writing_Level-Very_Difficult-orange.svg)]()
[![Tone: Free](https://img.shields.io/badge/Tone-Free-green.svg)]()

A distributed multi-agent swarm skill that enhances AI-generated writing into natural, human-grade prose using **[HumanizeAI.pro](https://www.humanizeai.pro/)**.

Operates on an optimal dedicated configuration:
- **Writing Level**: **Very difficult** (`academic`) - Designed for 0% AI detection on Turnitin & Copyleaks
- **Tone**: **Free** (`standard`)

This configuration creates the highest human authenticity scores across AI detectors (Copyleaks, GPTZero, Turnitin) while preserving 100% of facts, citations, code blocks, tables, and numerical data.

---

## Key Highlights

- **Live Site Auto-Discovery**: Automatically inspects the live HumanizeAI.pro frontend before execution to detect any renamed levels, new difficulty modes, or parameter changes, automatically selecting the highest humanization level.
- **Dynamic IP & Proxy Rotation**: Automatically harvests, validates, and rotates live HTTPS proxies to bypass Cloudflare Error 1015, IP rate limits, and 429 backoffs.
- **Strict Zero-Fallback Guarantee**: Eliminates silent reversion to raw AI text when API limits are encountered; retries across rotating proxies until 100% humanization is verified.
- **Optimal Writing Profile**: Pre-configured with **Writing Level: Very difficult** (`academic`) and **Tone: Free** for maximum stylistic depth and human burstiness.
- **Uncapped Document Length**: Decomposes long-form documents (research papers, essays, reports) into sentence-bounded semantic units of `<= 175` words.
- **Multi-Agent Swarm Execution**: Concurrently processes chunks with jittered backoff and isolated sessions.
- **Preserves Critical Content**:
  - Code blocks (` ```python `) and markdown tables (` | col | `) are preserved verbatim.
  - Markdown headings (`#`, `##`, `###`) and bullet hierarchies are cleanly retained.
- **Semantic Critic & Factual Audit**:
  - Automatically verifies preservation of citations (`(Author et al., Year)`), statistics (`98.4%`), dates, and technical abbreviations.
  - Surgically restores any citation or figure altered during rewriting without re-injecting AI perplexity.
- **Multi-Modality Ingestion**: Ingests `.txt`, `.md`, `.docx`, `.pdf`, and raw text.
- **Multi-Format Export**: Generates Markdown (`.md`), Microsoft Word (`.docx`), PDF (`.pdf`), or Academic LaTeX (`.tex`).
- **Universal Agent Skill**: Fully compatible with **Anthropic Claude Code**, **Google Antigravity**, **OpenAI Codex**, **OpenCode**, and **Hermes**.

---

## Quick Install (Give This Repo to Any Agent)

Simply give your AI agent this repository URL:
`https://github.com/porasnagar/humanizeai.pro-skill`

Or instruct your agent:
> *"Add the humanizeai-pro skill from https://github.com/porasnagar/humanizeai.pro-skill"*

### Universal One-Liner Installer
```bash
git clone https://github.com/porasnagar/humanizeai.pro-skill.git
cd humanizeai.pro-skill
python install.py
```
*(The automated installer detects installed agents on your system and registers the skill across all of them automatically).*

---

### Agent Installation Guide

| Agent | Direct Setup Command |
|---|---|
| **Anthropic Claude Code** | `git clone https://github.com/porasnagar/humanizeai.pro-skill.git ~/.claude/skills/humanizeai-pro` *(or run `python install.py`)* |
| **Google Antigravity** | `git clone https://github.com/porasnagar/humanizeai.pro-skill.git ~/.agents/skills/humanizeai-pro` |
| **OpenAI Codex / OpenCode** | `git clone https://github.com/porasnagar/humanizeai.pro-skill.git ~/.codex/skills/humanizeai-pro` |
| **Hermes Agent** | `git clone https://github.com/porasnagar/humanizeai.pro-skill.git ~/.hermes/skills/humanizeai-pro` |
| **Cursor / Custom Workspace** | `git clone https://github.com/porasnagar/humanizeai.pro-skill.git .cursor/skills/humanizeai-pro` |
| **Kimi Web / ChatGPT / Claude Web** | Provide the URL: `https://raw.githubusercontent.com/porasnagar/humanizeai.pro-skill/main/SKILL.md` |

---

## Command Line Usage

The CLI automatically runs with **Writing Level: Difficult** and **Tone: Free** by default:

```bash
# Basic Humanization (Markdown Output)
python -m humanizeai_pro document.md -o humanized.md

# Academic Research Paper to Word DOCX
python -m humanizeai_pro draft.docx -o final_paper.docx -f docx

# Publication-Grade PDF with 3 Concurrent Workers
python -m humanizeai_pro article.txt -o publication.pdf -f pdf -w 3

# Academic LaTeX Document
python -m humanizeai_pro paper.md -o paper.tex -f latex
```

### CLI Flags Reference

| Flag | Default | Description |
|---|---|---|
| `input` | *(Required)* | File path or raw text string |
| `-o, --output` | Auto-named | Path for the output file |
| `-l, --writing-level` | `advanced` | Writing level (`advanced` [Difficult], `academic`, `standard`, `simple`) |
| `-s, --style` | `standard` | Tone style (`standard` [Tone: Free]) |
| `-f, --format` | `md` | Target output format (`md`, `docx`, `pdf`, `latex`) |
| `-w, --workers` | `2` | Number of concurrent swarm workers |
| `--use-browser` | `False` | Enable Playwright browser automation mode |
| `--no-audit` | `False` | Skip semantic critic verification audit |
| `--proxy` | `None` | Optional HTTP/HTTPS proxy URL |
| `--rotate-ip` | `True` | Automatically validate and rotate active proxies to bypass rate limits |
| `--no-rotate-ip` | `False` | Disable automatic IP rotation |
| `--check-updates` | `False` | Force live site inspection to refresh difficulty and tone mappings |

---

## Python API Usage

```python
from humanizeai_pro import (
    HumanizerSwarm,
    SwarmConfig,
    DocumentExtractor,
    DocumentFormatter,
)

# 1. Ingest document
raw_text = DocumentExtractor.extract("research_paper.docx")

# 2. Configure swarm (Writing Level: Very difficult, Tone: Free)
config = SwarmConfig(
    workers=2,
    writing_level="academic",  # Very difficult (0% AI detection on Turnitin)
    style="standard",          # Tone: Free
    max_chunk_words=175,
    delay_between_requests=0.8,
    enable_jitter=True,
    audit_facts=True,
)

# 3. Execute swarm humanization
swarm = HumanizerSwarm(config)
result = swarm.humanize(raw_text)

print(f"Humanized {result.input_word_count} -> {result.output_word_count} words in {result.elapsed_time:.2f}s")

# 4. Inspect audit findings
if result.audit:
    print("Citations verified:", len(result.audit.preserved_citations))
    print("Statistics verified:", len(result.audit.preserved_numbers))

# 5. Export to Word DOCX or PDF
output_file = DocumentFormatter.export(result.humanized_text, "output.docx", format_type="docx")
print("Saved to:", output_file)
```

---

## License

MIT License. Designed for ethical writing enhancement, academic editing, and research synthesis.
