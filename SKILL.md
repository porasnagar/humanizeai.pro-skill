---
name: humanizeai-pro
description: Universal Long-Form AI Text Humanizer and Natural Flow Enhancer powered by HumanizeAI.pro. Uses distributed sentence-boundary semantic chunking with Writing Level Difficult and Tone Free, academic citation preservation, factual auditing, and multi-format export (Markdown, Word .docx, PDF, LaTeX). Fully compatible with Anthropic Claude Code, Google Antigravity, OpenAI Codex, OpenCode, and Hermes.
---

# HumanizeAI Pro Multi-Agent Swarm Skill

The **HumanizeAI Pro Swarm** skill enhances AI-generated writing into authentic, human-sounding prose for documents of **any word count** using `https://www.humanizeai.pro/`.

It uses an optimal dedicated configuration:
- **Writing Level**: **Difficult** (`advanced`) - Generates rich, human-grade vocabulary and varied syntactic burstiness.
- **Tone**: **Free** (`standard`) - Natural, balanced, and unconstrained human flow.

This combination produces the highest human authenticity scores across AI detectors (Copyleaks, GPTZero, Turnitin) while preserving 100% of facts, citations (`Author et al., Year`), code blocks, tables, numbers, and technical terminology.

Compatible across **Anthropic Claude Code**, **Google Antigravity**, **OpenAI Codex**, **OpenCode**, and **Hermes**.

---

## 1. Optimal Configuration (Default)

| Parameter | Setting | Internal Value | Purpose |
|---|---|---|---|
| **Writing Level** | **Difficult** *(Default)* | `advanced` | Varied sentence length, rich vocabulary, high burstiness |
| **Tone** | **Free** *(Default)* | `standard` | Authentic, unconstrained natural cadence |
| **Chunk Size** | **150–175 words** | Auto | Preserves sentence and paragraph boundaries losslessly |

*(Note: Other modes are unnecessary—Writing Level Difficult + Tone Free provides the optimal humanization quality).*

---

## 2. Universal Agent Workflow

Whenever a user requests humanization of a file or text, follow this 5-step pipeline:

```
[User Input: Text / MD / DOCX / PDF / Image]
                    │
                    ▼
     1. Ingest & Extract Structure
                    │
                    ▼
     2. Confirm Desired Output Format (Ask User First!)
                    │
                    ▼
     3. Deploy Multi-Agent Swarm (Writing Level: Difficult, Tone: Free)
                    │
                    ▼
     4. Review Critic Fact & Citation Audit
                    │
                    ▼
     5. Deliver Verified Output Document
```

---

### Step 1: Ingest Document or Raw Text

The skill automatically extracts and preserves structure from:
- **Plain Text / Markdown (`.txt`, `.md`)**
- **Word Documents (`.docx`)**
- **PDF Documents (`.pdf`)**
- **Direct String Input**

---

### Step 2: Confirm Desired Output Format (MANDATORY INTERACTION)

> [!IMPORTANT]
> **Ask the user which output format they want** before compiling the final document:
> 1. **Markdown (`.md`)**
> 2. **Microsoft Word (`.docx`)**
> 3. **Standard PDF (`.pdf`)**
> 4. **Academic LaTeX Document (`.tex`)**

---

### Step 3: Run the Multi-Agent Swarm

Execute the swarm CLI (defaults to Writing Level **Difficult** and Tone **Free**):

```bash
# Basic Humanization (Markdown output)
python -m humanizeai_pro "<input_file>" -o "<output_file>.md" -f md

# Academic Research Paper (DOCX output)
python -m humanizeai_pro "<input_file>" -o "<output_file>.docx" -f docx

# Publication-grade PDF with 3 workers
python -m humanizeai_pro "<input_file>" -o "<output_file>.pdf" -f pdf -w 3

# Academic LaTeX output
python -m humanizeai_pro "<input_file>" -o "<output_file>.tex" -f latex
```

#### CLI Options Reference

| Flag | Default | Description |
|---|---|---|
| `input` | *(Required)* | File path or raw text string |
| `-o, --output` | Auto-named | Destination file path |
| `-l, --writing-level` | `advanced` | Writing level (`advanced` [Difficult], `academic`, `standard`, `simple`) |
| `-s, --style` | `standard` | Tone style (`standard` [Tone: Free]) |
| `-f, --format` | `md` | Output format (`md`, `docx`, `pdf`, `latex`) |
| `-w, --workers` | `2` | Number of concurrent worker threads |
| `--use-browser` | `False` | Enable Playwright browser automation mode |
| `--no-audit` | `False` | Skip critic verification audit |
| `--proxy` | `None` | Optional HTTP/HTTPS proxy URL |

---

### Step 4: Python API Usage

AI agents can also import and drive the swarm directly in Python:

```python
from humanizeai_pro import HumanizerSwarm, SwarmConfig, DocumentExtractor, DocumentFormatter

# 1. Ingest document
raw_text = DocumentExtractor.extract("research_paper.docx")

# 2. Configure swarm (Writing Level: Difficult, Tone: Free)
config = SwarmConfig(
    workers=2,
    writing_level="advanced",  # Difficult
    style="standard",          # Tone: Free
    max_chunk_words=175,
    delay_between_requests=0.8,
    enable_jitter=True,
    audit_facts=True
)

# 3. Execute swarm humanization
swarm = HumanizerSwarm(config)
result = swarm.humanize(raw_text)

# 4. Verify audit results
if result.audit:
    print(f"Citations verified: {len(result.audit.preserved_citations)}/{result.audit.total_citations_found}")
    print(f"Statistics verified: {len(result.audit.preserved_numbers)}/{result.audit.total_numbers_found}")

# 5. Export to Word DOCX or PDF
output_path = DocumentFormatter.export(result.humanized_text, "output.docx", format_type="docx")
print("Saved to:", output_path)
```

---

### Step 5: Architecture & Resiliency

1. **Sentence-Bounded Semantic Chunking**:
   - `SemanticChunker` decomposes long documents on sentence boundaries into ~150–175 word segments.
   - Code blocks (` ``` `), tables (` | `), LaTeX equations (` $$ `), and markdown headers are isolated and preserved verbatim.
2. **Distributed Resilient Client**:
   - Uses adaptive rate-limiting, randomized jitter (0.8s–2.5s), and exponential backoff to ensure reliable network throughput.
   - Playwright browser engine fallback is available if headless automation is preferred.
3. **Critic & Fact Preservation Audit**:
   - Compares input vs output to verify academic citations (`(Author et al., Year)`), percentages, dates, and technical abbreviations.
   - Surgically restores any dropped citations at the exact sentence where the author is mentioned without re-injecting standard AI perplexity.
