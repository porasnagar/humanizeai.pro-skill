# HumanizeAI Pro Multi-Agent Swarm

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8%2B-brightgreen.svg)](https://python.org)
[![Agents: Antigravity | Claude Code | Codex | Hermes](https://img.shields.io/badge/Agents-Universal_Skill-purple.svg)]()
[![Free Tier Bypass: 200 Words -> Unlimited](https://img.shields.io/badge/Bypass-Free_Tier_Unlimited-success.svg)]()

A distributed multi-agent swarm skill that transforms AI-generated content into 100% human-sounding prose using **[HumanizeAI.pro](https://www.humanizeai.pro/)**.

While HumanizeAI.pro's public interface limits free outputs to **200 words per request**, this skill breaks documents of **arbitrary length** (thousands of words, complete papers, reports) into coordinated semantic units, humanizes them concurrently across worker agents, defeats anti-bot and rate-limiting controls, and reassembles the document with 100% preservation of citations, tables, code, and numerical figures.

---

## Key Features

- **Free-Tier 200-Word Limit Bypass**: Eliminates output truncation and locked words by coordinating semantic chunks of `<= 175` words.
- **Uncapped Document Length**: Process short paragraphs or 10,000+ word dissertations in minutes.
- **Multi-Agent Swarm Concurrency**: Dispatches chunks across parallel worker agents with jittered backoff and isolated sessions.
- **Deep Anti-Bot & WAF Evasion**:
  - Direct HTTP engine with randomized modern browser fingerprints (Chrome 124, Edge 123, Client Hints).
  - Headless **Playwright stealth browser fallback** with CDP anti-automation flag stripping (`navigator.webdriver = undefined`).
- **Semantic Critic & Factual Audit**:
  - Automatically verifies preservation of citations (`(Author et al., Year)`), statistics (`98.4%`), dates, and technical abbreviations.
  - Surgically restores any citation or figure altered during rewriting without touching humanized prose.
- **Preserves Complex Structure**:
  - Code blocks (` ```python `) and markdown tables (` | col | `) are preserved verbatim.
  - Markdown headings (`#`, `##`, `###`) and bullet hierarchies are cleanly retained.
- **Multi-Modality Ingestion**: Ingests `.txt`, `.md`, `.docx`, `.pdf`, and raw text.
- **Multi-Format Export**: Generates Markdown (`.md`), Microsoft Word (`.docx`), PDF (`.pdf`), or Academic LaTeX (`.tex`).
- **Universal Agent Skill**: Ready for **Google Antigravity**, **Claude Code**, **OpenAI Codex**, **OpenCode**, and **Hermes**.

---

## Architecture

```
                          ┌────────────────────────┐
                          │   Input Source File    │
                          │ (.txt/.md/.docx/.pdf)  │
                          └───────────┬────────────┘
                                      │
                                      ▼
                        ┌────────────────────────────┐
                        │ DocumentExtractor & Chunker│
                        │ (Semantic units <= 175 w)  │
                        └─────────────┬──────────────┘
                                      │
                 ┌────────────────────┼────────────────────┐
                 ▼                    ▼                    ▼
        ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
        │ Swarm Worker 1  │  │ Swarm Worker 2  │  │ Swarm Worker N  │
        │ Session UUID #1 │  │ Session UUID #2 │  │ Session UUID #N │
        └────────┬────────┘  └────────┬────────┘  └────────┬────────┘
                 │                    │                    │
                 └────────────────────┼────────────────────┘
                                      │
                         [ Direct HTTP /api/process ]
                         [ Fallback: Stealth Browser]
                                      │
                                      ▼
                        ┌────────────────────────────┐
                        │      DocumentStitcher      │
                        │ (Lossless structural merge)│
                        └─────────────┬──────────────┘
                                      │
                                      ▼
                        ┌────────────────────────────┐
                        │   Semantic Critic Audit    │
                        │ (Citations/Numbers Verify) │
                        └─────────────┬──────────────┘
                                      │
                                      ▼
                        ┌────────────────────────────┐
                        │     DocumentFormatter      │
                        │    (MD / DOCX / PDF / TeX) │
                        └────────────────────────────┘
```

---

## Quick Install (Give This Repo to Any Agent)

Simply give your AI agent this repository URL:
`https://github.com/porasnagar/humanizeai.pro-skill`

Or instruct your agent:
> *"Install the humanizer skill from https://github.com/porasnagar/humanizeai.pro-skill"*

### Automatic Universal Installer
```bash
git clone https://github.com/porasnagar/humanizeai.pro-skill.git
cd humanizeai.pro-skill
python install.py
```
*(The automated installer detects all installed agents on your machine and registers the skill across all of them automatically!)*

---

### Agent-Specific Installation Commands

| Agent | Direct One-Liner Install |
|---|---|
| **Google Antigravity** | `git clone https://github.com/porasnagar/humanizeai.pro-skill.git ~/.agents/skills/humanizeai-pro` |
| **Claude Code** | `git clone https://github.com/porasnagar/humanizeai.pro-skill.git ~/.claude/skills/humanizeai-pro` |
| **OpenAI Codex / OpenCode** | `git clone https://github.com/porasnagar/humanizeai.pro-skill.git ~/.codex/skills/humanizeai-pro` |
| **Hermes Agent** | `git clone https://github.com/porasnagar/humanizeai.pro-skill.git ~/.hermes/skills/humanizeai-pro` |
| **Cursor / Custom Project** | `git clone https://github.com/porasnagar/humanizeai.pro-skill.git .cursor/skills/humanizeai-pro` |
| **Kimi Web / ChatGPT / Claude Web** | Provide the URL: `https://raw.githubusercontent.com/porasnagar/humanizeai.pro-skill/main/SKILL.md` |

---

## Prerequisites (Optional Fallback)

Core dependencies are automatically installed by `install.py` or via `pip`:
```bash
pip install -r requirements.txt
```

*(Optional: To enable automated stealth browser fallback if Cloudflare challenges trigger)*:
```bash
playwright install chromium
```

---

## Supported Rewriting Styles

| Style | Purpose | Best Used For |
|---|---|---|
| `standard` | Balanced natural flow (Default) | General essays, blog posts, articles, reports |
| `academic` | Scholarly vocabulary & formal cadence | Research papers, literature reviews, theses |
| `simple` | Clear, plain English | Explanatory guides, technical documentation |
| `flowing` | Narrative, rhythmic prose | Creative non-fiction, storytelling, speeches |
| `formal` | Polished corporate tone | Executive memos, proposals, formal briefs |
| `informal` | Casual conversational dialogue | Forum responses, social media, newsletters |
| `expand` | Elaborates ideas with greater depth | Short drafts, high-level bullet expansions |
| `shorten` | Trims fluff while retaining core facts | Abstracts, summaries, character-limited copy |

---

## Command Line Usage

### Basic Humanization (Markdown Output)
```bash
python -m humanizeai_pro document.md -o humanized.md -s standard -f md
```

### Academic Research Paper to Word DOCX
```bash
python -m humanizeai_pro draft.docx -o final_paper.docx -s academic -f docx
```

### Publication PDF with 3 Concurrent Workers
```bash
python -m humanizeai_pro article.txt -o publication.pdf -s standard -f pdf -w 3
```

### Academic LaTeX Document
```bash
python -m humanizeai_pro paper.md -o paper.tex -s academic -f latex
```

### Force Playwright Stealth Browser Mode
```bash
python -m humanizeai_pro document.pdf -o output.docx -s standard -f docx --use-browser
```

### CLI Flags Reference

| Flag | Default | Description |
|---|---|---|
| `input` | *(Required)* | File path or raw text string |
| `-o, --output` | Auto-named | Path for the output file |
| `-s, --style` | `standard` | Rewrite style (`standard`, `academic`, `simple`, `flowing`, `formal`, `informal`, `expand`, `shorten`) |
| `-f, --format` | `md` | Target output format (`md`, `docx`, `pdf`, `latex`) |
| `-w, --workers` | `2` | Number of concurrent swarm workers |
| `--use-browser` | `False` | Force Playwright stealth browser engine |
| `--no-audit` | `False` | Skip semantic critic verification audit |
| `--proxy` | `None` | Optional HTTP/HTTPS proxy URL |

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

# 2. Configure swarm parameters
config = SwarmConfig(
    workers=2,
    style="academic",
    max_chunk_words=175,
    delay_between_requests=0.8,
    enable_jitter=True,
    use_browser_fallback=True,
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

## Agent Integration (Antigravity, Claude Code, Codex, Hermes)

This repository includes a pre-configured `SKILL.md` compliant with universal agent specifications.

- **Antigravity IDE**: Automatically discovered in `.agents/skills/humanizeai-pro/` or workspace root.
- **Claude Code**: Invoke directly via bash tool: `python -m humanizeai_pro <file>`.
- **OpenAI Codex / Hermes**: Import `HumanizerSwarm` in any Python environment or run the CLI.

---

## License

MIT License. Designed for ethical writing enhancement, academic editing, and research synthesis.
