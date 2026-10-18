#!/usr/bin/env python3
"""
Universal Cross-Agent Installer for HumanizeAI Pro Swarm
Auto-detects and installs the skill for:
- Google Antigravity (~/.gemini/config/skills & .agents/skills)
- Anthropic Claude Code (~/.claude/skills)
- OpenAI Codex & OpenCode (~/.codex/skills & ~/.config/opencode/skills)
- Hermes Agent (~/.hermes/skills)
- Cursor & Custom Workspaces (.cursor/skills)
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

SKILL_NAME = "humanizeai-pro"
REPO_ROOT = Path(__file__).resolve().parent

AGENT_SKILL_PATHS = [
    # Global Antigravity Config
    Path.home() / ".gemini" / "config" / "skills" / SKILL_NAME,
    Path.home() / ".gemini" / "config" / "skills" / "humanizer",
    # Global Universal Agents
    Path.home() / ".agents" / "skills" / SKILL_NAME,
    # Local workspace Antigravity (if in project)
    REPO_ROOT.parent / ".agents" / "skills" / SKILL_NAME,
    # Claude Code
    Path.home() / ".claude" / "skills" / SKILL_NAME,
    # Codex / OpenCode
    Path.home() / ".codex" / "skills" / SKILL_NAME,
    Path.home() / ".config" / "opencode" / "skills" / SKILL_NAME,
    # Hermes
    Path.home() / ".hermes" / "skills" / SKILL_NAME,
]

LEGACY_HUMANIZER_PATHS = [
    Path.home() / ".claude" / "skills" / "humanizer",
    Path.home() / ".hermes" / "skills" / "humanizer",
    Path.home() / ".config" / "opencode" / "skills" / "humanizer",
]


def cleanup_legacy():
    print("[*] Cleaning up old legacy humanizer installations...")
    for old_path in LEGACY_HUMANIZER_PATHS:
        if old_path.exists():
            try:
                shutil.rmtree(old_path)
                print(f"[+] Removed legacy humanizer from: {old_path}")
            except Exception as e:
                print(f"[!] Warning: Could not remove {old_path}: {e}")


def install_dependencies():
    req_file = REPO_ROOT / "requirements.txt"
    if req_file.exists():
        print(f"[*] Installing dependencies from {req_file}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(req_file)])
            print("[+] Dependencies installed successfully.")
        except Exception as e:
            print(f"[!] Warning: Pip install failed ({e}). Please install requirements manually.")


def install_skill():
    print(f"============================================================")
    print(f"     HumanizeAI Pro Universal Skill Installer               ")
    print(f"============================================================")

    installed_targets = []

    for target_dir in AGENT_SKILL_PATHS:
        parent_agent = target_dir.parent.parent
        is_global = ".agents" in str(target_dir) or ".gemini" in str(target_dir)

        if parent_agent.exists() or is_global:
            try:
                target_dir.mkdir(parents=True, exist_ok=True)

                # Determine skill name for SKILL.md
                skill_id = target_dir.name
                skill_content = (REPO_ROOT / "SKILL.md").read_text(encoding="utf-8")
                if skill_id != SKILL_NAME:
                    skill_content = skill_content.replace(f"name: {SKILL_NAME}", f"name: {skill_id}")

                (target_dir / "SKILL.md").write_text(skill_content, encoding="utf-8")

                # Copy scripts directory
                if (REPO_ROOT / "scripts").exists():
                    scripts_dst = target_dir / "scripts"
                    if scripts_dst.exists():
                        shutil.rmtree(scripts_dst)
                    shutil.copytree(REPO_ROOT / "scripts", scripts_dst)

                # Copy humanizeai_pro package
                if (REPO_ROOT / "humanizeai_pro").exists():
                    pkg_dst = target_dir / "humanizeai_pro"
                    if pkg_dst.exists():
                        shutil.rmtree(pkg_dst)
                    shutil.copytree(REPO_ROOT / "humanizeai_pro", pkg_dst)

                print(f"[+] Installed skill into: {target_dir}")
                installed_targets.append(str(target_dir))
            except Exception as e:
                print(f"[!] Could not install into {target_dir}: {e}")

    # Also install locally in editable mode
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", str(REPO_ROOT)])
        print("[+] Registered CLI package 'humanizeai-pro' into Python environment.")
    except Exception:
        pass

    print(f"\n[+] Skill installation complete! Configured for {len(installed_targets)} agent directories.")
    print(f"[*] You can now invoke the skill across Antigravity, Claude Code, Codex, and Hermes.")


if __name__ == "__main__":
    cleanup_legacy()
    install_dependencies()
    install_skill()
