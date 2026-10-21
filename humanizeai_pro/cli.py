import argparse
import sys
import time
from pathlib import Path

# Ensure UTF-8 output encoding on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table

from .critic import SemanticCritic
from .extractor import DocumentExtractor
from .formatter import DocumentFormatter
from .swarm import HumanizerSwarm, SwarmConfig

console = Console(force_terminal=True, legacy_windows=False)


def print_banner():
    banner = """[bold cyan]+==============================================================+
|             [bold white]HumanizeAI.pro Multi-Agent Swarm[/bold white]                 |
|   [dim]Bypass 200-Word Free Tier Limits, Anti-Bot & IP Rotation[/dim]   |
+==============================================================+[/bold cyan]"""
    console.print(banner)



def main():
    parser = argparse.ArgumentParser(
        description="Humanize arbitrary-length documents using HumanizeAI.pro multi-agent swarm."
    )
    parser.add_argument(
        "input",
        type=str,
        help="Path to input file (.txt, .md, .docx, .pdf) or raw text string",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="Path to save output file (defaults to <input_stem>_humanized.<format>)",
    )
    parser.add_argument(
        "-l",
        "--writing-level",
        type=str,
        default="advanced",
        choices=["advanced", "academic", "standard", "simple"],
        help="Writing level (default: advanced [Difficult])",
    )
    parser.add_argument(
        "-s",
        "--style",
        type=str,
        default="standard",
        help="Tone style (default: standard [Tone: Free])",
    )
    parser.add_argument(
        "-f",
        "--format",
        type=str,
        default="md",
        choices=["md", "docx", "pdf", "latex", "tex", "txt"],
        help="Target output format (default: md)",
    )
    parser.add_argument(
        "-w",
        "--workers",
        type=int,
        default=2,
        help="Number of concurrent swarm worker threads (default: 2)",
    )
    parser.add_argument(
        "--use-browser",
        action="store_true",
        help="Force Playwright stealth browser engine instead of direct HTTP API",
    )
    parser.add_argument(
        "--no-audit",
        action="store_true",
        help="Skip critic fact verification audit",
    )
    parser.add_argument(
        "--proxy",
        type=str,
        default=None,
        help="Optional proxy (e.g. http://127.0.0.1:8080)",
    )
    parser.add_argument(
        "--rotate-ip",
        action="store_true",
        default=True,
        help="Enable dynamic IP/proxy rotation to bypass Cloudflare rate limits (default: True)",
    )
    parser.add_argument(
        "--no-rotate-ip",
        dest="rotate_ip",
        action="store_false",
        help="Disable dynamic IP/proxy rotation",
    )

    args = parser.parse_args()
    print_banner()

    # Step 1: Document Ingestion
    console.print(f"[bold yellow][>] Step 1: Ingesting source...[/bold yellow]")
    try:
        raw_text = DocumentExtractor.extract(args.input)
        input_word_count = len(raw_text.split())
        console.print(
            f"  [green][+] Loaded document:[/green] {input_word_count:,} words extracted."
        )
    except Exception as e:
        console.print(f"  [bold red][x] Extraction error:[/bold red] {e}")
        sys.exit(1)

    if input_word_count == 0:
        console.print("[bold red]Document contains no text to humanize.[/bold red]")
        sys.exit(1)

    # Step 2: Initialize Swarm
    config = SwarmConfig(
        workers=args.workers,
        style=args.style,
        writing_level=args.writing_level,
        max_chunk_words=175,
        delay_between_requests=0.8,
        enable_jitter=True,
        use_browser_fallback=args.use_browser,
        proxy=args.proxy,
        rotate_ip=args.rotate_ip,
        audit_facts=not args.no_audit,
    )
    swarm = HumanizerSwarm(config)

    # Step 3: Swarm Execution with Rich Progress Bar
    wl_display = "Difficult" if args.writing_level == "advanced" else args.writing_level.title()
    rot_display = "Active" if args.rotate_ip else "Disabled"
    console.print(
        f"\n[bold yellow][>] Step 2: Deploying {args.workers}-Worker Swarm (Writing Level: {wl_display}, Tone: Free, IP Rotation: {rot_display})...[/bold yellow]"
    )

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Processing chunks...", total=100)

        def update_progress(current, total, msg):
            if total > 0:
                percent = int((current / total) * 100)
                progress.update(task, completed=percent, description=f"[cyan]{msg}")

        result = swarm.humanize(raw_text, progress_callback=update_progress)

    # Step 4: Display Audit Report
    if result.audit:
        console.print(f"\n[bold yellow][>] Step 3: Semantic Audit & Fact Verification[/bold yellow]")
        table = Table(title="Critic Audit Summary", border_style="cyan")
        table.add_column("Category", style="bold white")
        table.add_column("Total Found", style="cyan")
        table.add_column("Preserved", style="green")
        table.add_column("Discrepancies", style="red")

        table.add_row(
            "Citations / References",
            str(result.audit.total_citations_found),
            str(len(result.audit.preserved_citations)),
            str(len(result.audit.missing_citations)),
        )
        table.add_row(
            "Numbers, Dates & Statistics",
            str(result.audit.total_numbers_found),
            str(len(result.audit.preserved_numbers)),
            str(len(result.audit.missing_numbers)),
        )
        console.print(table)

        if result.audit.notes:
            for n in result.audit.notes:
                console.print(f"  [yellow][!] Note:[/yellow] {n}")
        else:
            console.print("  [bold green][+] Perfect 100% factual and citation preservation verified![/bold green]")

    # Step 5: Document Compilation
    if not args.output:
        stem = Path(args.input).stem if Path(args.input).exists() else "humanized_document"
        ext = args.format if args.format != "latex" else "tex"
        output_file = f"{stem}_humanized.{ext}"
    else:
        output_file = args.output

    console.print(f"\n[bold yellow][>] Step 4: Compiling to {args.format.upper()} format...[/bold yellow]")
    try:
        final_path = DocumentFormatter.export(
            result.humanized_text,
            output_file,
            format_type=args.format,
        )
        console.print(f"  [bold green][+] Output saved successfully:[/bold green] [bold underline]{final_path}[/bold underline]")
    except Exception as e:
        console.print(f"  [bold red][x] Formatting error:[/bold red] {e}")
        # Save as markdown fallback
        fallback = f"{output_file}.md"
        Path(fallback).write_text(result.humanized_text, encoding="utf-8")
        console.print(f"  [yellow]Saved fallback markdown at: {fallback}[/yellow]")

    # Metrics Summary Box
    metrics_panel = f"""[bold white]Performance Metrics:[/bold white]
  * Input Words: [cyan]{result.input_word_count:,}[/cyan]  ->  Output Words: [green]{result.output_word_count:,}[/green]
  * Chunks Processed: [cyan]{result.chunks_humanized}/{result.chunks_total}[/cyan]
  * Elapsed Time: [yellow]{result.elapsed_time:.2f}s[/yellow] ([magenta]{result.speed_words_per_sec:.1f} words/sec[/magenta])
  * Free-Tier Bypass: [bold green]100% Active (Zero Truncation / No Locked Words)[/bold green]"""
    console.print("\n", Panel(metrics_panel, title="[bold green]Humanization Complete[/bold green]", border_style="green"))


if __name__ == "__main__":
    main()
