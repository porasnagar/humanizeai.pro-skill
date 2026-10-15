---
name: humanizeai-pro
description: Universal Multi-Agent Swarm AI Text Humanizer powered by HumanizeAI.pro. Bypasses the 200-word free tier limit for documents of arbitrary length by coordinating a distributed chunking swarm with built-in Cloudflare WAF/Turnstile evasion, automated stealth browser fallback, semantic fact preservation (citations, numbers, dates), and multi-format compilation (Markdown, Word .docx, PDF, LaTeX). Compatible across Google Antigravity, Claude Code, OpenAI Codex, OpenCode, and Hermes.
---

# HumanizeAI Pro Multi-Agent Swarm Skill

The **HumanizeAI Pro Swarm** skill humanizes AI-generated text of **any word count** for 100% free using `https://www.humanizeai.pro/`.

While HumanizeAI.pro's public interface limits free outputs to 200 words per run, this skill deploys a **coordinated multi-agent swarm** that:
1. Deconstructs long documents into optimal ~150-175 word semantic units (preserving code blocks, LaTeX, tables, and markdown headers verbatim).
2. Humanizes all chunks in parallel through HumanizeAI.pro's native API using rotating browser identities, dynamic session IDs, and zero-truncation payloads.
3. Automatically defeats anti-bot and rate-limiting defenses with exponential jitter and headless stealth Playwright browser fallback.
4. Losslessly stitches the document back together with flawless structural cohesion.
5. Performs surgical Critic audits to ensure 100% preservation of citations (`(Author et al., Year)`), statistics, dates, and technical terminology.
6. Compiles the verified result into Markdown (`.md`), Word (`.docx`), PDF (`.pdf`), or LaTeX (`.tex`).

Compatible across **Google Antigravity**, **Claude Code**, **OpenAI Codex**, **OpenCode**, and **Hermes**.

---

## 1. Supported Humanization Styles

| Style | Purpose | Best Used For |
|---|---|---|
| `standard` | Balanced human rewrite (Default) | General essays, blog posts, articles, reports |
| `academic` | Scholarly vocabulary & formal flow | Research papers, literature reviews, dissertations |
| `simple` | Clear, concise, plain English | Explanatory guides, documentation, emails |
| `flowing` | Highly narrative, rhythmic cadence | Creative non-fiction, storytelling, speeches |
| `formal` | Professional, business-level tone | Corporate memos, executive summaries, proposals |
| `informal` | Conversational, casual dialogue | Social media, forum answers, casual newsletters |
| `expand` | Elaborates ideas with richer detail | Under-developed paragraphs, brainstorming drafts |
| `shorten` | Trims fluff while keeping substance | Summaries, abstracts, character-constrained texts |

---

## 2. Universal Agent Workflow

Whenever a user requests humanization of a file or text, follow this strict 5-step pipeline:

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
     3. Deploy Multi-Agent Swarm (python -m humanizeai_pro)
                    │
                    ▼
     4. Review Critic Fact Audit
                    │
                    ▼
     5. Deliver Verified Output Document
```

---

### Step 1: Ingest Document or Raw Text

The skill automatically handles any input format:
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

Execute the swarm CLI:

```bash
# Basic Humanization (Markdown output)
python -m humanizeai_pro "<input_file>" -o "<output_file>.md" -s standard -f md

# Academic Research Paper (DOCX output)
python -m humanizeai_pro "<input_file>" -o "<output_file>.docx" -s academic -f docx

# Publication-grade PDF with 3 workers
python -m humanizeai_pro "<input_file>" -o "<output_file>.pdf" -s standard -f pdf -w 3

# Academic LaTeX output
python -m humanizeai_pro "<input_file>" -o "<output_file>.tex" -s academic -f latex
```

#### CLI Flags Reference

| Flag | Default | Description |
|---|---|---|
| `input` | *(Required)* | File path or raw text string |
| `-o, --output` | Auto-named | Destination file path |
| `-s, --style` | `standard` | Style (`standard`, `academic`, `simple`, `flowing`, `formal`, `informal`, `expand`, `shorten`) |
| `-f, --format` | `md` | Output format (`md`, `docx`, `pdf`, `latex`) |
| `-w, --workers` | `2` | Number of concurrent worker threads |
| `--use-browser` | `False` | Force Playwright stealth browser engine |
| `--no-audit` | `False` | Skip critic verification audit |
| `--proxy` | `None` | Optional HTTP/HTTPS proxy URL |

---

### Step 4: Python API Usage (Inside Agent Scripts or MCP Tools)

AI agents can also import and drive the swarm directly in Python:

```python
from humanizeai_pro import HumanizerSwarm, SwarmConfig, DocumentExtractor, DocumentFormatter

# 1. Ingest document
raw_text = DocumentExtractor.extract("research_paper.docx")

# 2. Configure swarm
config = SwarmConfig(
    workers=2,
    style="academic",
    max_chunk_words=175,
    delay_between_requests=0.8,
    enable_jitter=True,
    use_browser_fallback=True,
    audit_facts=True
)

# 3. Execute swarm humanization
swarm = HumanizerSwarm(config)
result = swarm.humanize(raw_text)

print(f"Humanized {result.input_word_count} -> {result.output_word_count} words in {result.elapsed_time:.2f}s")

# 4. Check critic audit
if result.audit:
    print(f"Citations preserved: {len(result.audit.preserved_citations)}/{result.audit.total_citations_found}")
    print(f"Statistics preserved: {len(result.audit.preserved_numbers)}/{result.audit.total_numbers_found}")

# 5. Export to Word DOCX or PDF
output_path = DocumentFormatter.export(result.humanized_text, "output.docx", format_type="docx")
print("Saved to:", output_path)
```

---

### Step 5: How the Free-Tier & Anti-Bot Bypass Works Under the Hood

1. **Free Tier 200-Word Boundary Bypass**:
   - `humanizeai.pro` only enforces truncation/locking when a single request exceeds 200 words.
   - The `SemanticChunker` dynamically segments documents on sentence boundaries into safe ~150-175 word chunks while preserving code blocks, markdown tables, and headers verbatim.
   - Every single chunk returns 100% unlocked text without requiring any paid account or API key.
2. **Anti-Bot & Rate-Limit Defense**:
   - Rotates realistic modern browser fingerprints (Chrome 124, Edge 123, macOS/Windows Client Hints).
   - Generates isolated session UUIDs for each worker request.
   - Applies random exponential jitter (0.8s - 2.5s) to stay beneath WAF threshold alarms.
3. **Automated Stealth Browser Fallback**:
   - If direct HTTP ever encounters a Cloudflare challenge or 403 status, the worker immediately activates `BrowserHumanizeClient` using headless Playwright with deep evasion patches (`navigator.webdriver = undefined`, mocked plugins, randomized viewports).
4. **Agent-as-Critic Fact Preservation**:
   - Verifies all citations (`Vaswani et al. (2017)`), percentages (`14.8%`), dates, and technical abbreviations.
   - Performs surgical restoration if any citation or figure was altered during rewriting.
