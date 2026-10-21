"""
Automated GitHub Skill Updater for HumanizeAI.pro
Keeps the skill synchronized with the latest upstream repository improvements from
https://github.com/porasnagar/humanizeai.pro-skill.

Automatically checks for updates on GitHub, pulls latest changes, and synchronizes
across all detected agent environments (Google Antigravity, Claude Code, Codex, Hermes).
"""

import json
import logging
import os
import shutil
import ssl
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger("humanizeai_pro.updater")

GITHUB_REPO = "porasnagar/humanizeai.pro-skill"
GITHUB_COMMITS_API = f"https://api.github.com/repos/{GITHUB_REPO}/commits/main"
VERSION_CACHE_FILE = os.path.join(os.path.expanduser("~"), ".humanizeai_version.json")
CHECK_INTERVAL_SECONDS = 43200  # 12 hours between background checks


class SkillUpdater:
    """Manages automatic checks and updates from https://github.com/porasnagar/humanizeai.pro-skill."""

    def __init__(self, repo_dir: Optional[Path] = None):
        self.repo_dir = repo_dir or self._discover_repo_root()
        self.cache_file = VERSION_CACHE_FILE

    @staticmethod
    def _discover_repo_root() -> Path:
        """Find the root directory of the humanizeai-pro repository or skill."""
        # Check current file path
        current_path = Path(__file__).resolve().parent.parent
        if (current_path / ".git").exists():
            return current_path

        # Check standard known locations
        candidates = [
            Path.home() / "humanize-ai-pro-skill",
            Path.home() / ".agents" / "skills" / "humanizeai-pro",
            Path.home() / ".gemini" / "config" / "skills" / "humanizer",
            current_path,
        ]
        for c in candidates:
            if c.exists() and ((c / ".git").exists() or (c / "SKILL.md").exists()):
                return c

        return current_path

    def _get_local_commit(self) -> Optional[str]:
        """Get the current local git commit hash if running in a git repo."""
        if self.repo_dir and (self.repo_dir / ".git").exists():
            try:
                res = subprocess.run(
                    ["git", "-C", str(self.repo_dir), "rev-parse", "HEAD"],
                    capture_output=True,
                    text=True,
                    timeout=3,
                )
                if res.returncode == 0 and res.stdout.strip():
                    return res.stdout.strip()
            except Exception:
                pass

        # Check version cache
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("current_commit")
            except Exception:
                pass

        return None

    def _get_remote_commit(self, timeout: float = 4.0) -> Optional[Tuple[str, str, str]]:
        """Query latest GitHub commit hash without API rate limits.
        Uses git ls-remote, Atom feed, and GitHub REST API fallbacks.
        Returns: (sha, short_msg, date)
        """
        # Strategy 1: git ls-remote (fastest, zero rate limits)
        try:
            res = subprocess.run(
                ["git", "ls-remote", f"https://github.com/{GITHUB_REPO}.git", "HEAD"],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            if res.returncode == 0 and res.stdout.strip():
                sha = res.stdout.strip().split()[0]
                if len(sha) == 40:
                    return sha, "Latest commit on main", ""
        except Exception:
            pass

        # Strategy 2: GitHub Atom RSS Feed (zero rate limits, works even behind firewalls)
        ctx = ssl._create_unverified_context()
        try:
            atom_url = f"https://github.com/{GITHUB_REPO}/commits/main.atom"
            req = urllib.request.Request(atom_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
                atom = r.read().decode("utf-8", errors="ignore")
                import re
                match = re.search(r"Commit/([0-9a-f]{40})", atom)
                if match:
                    title_match = re.search(r"<title>([^<]+)</title>", atom)
                    msg = title_match.group(1) if title_match else "Latest commit"
                    return match.group(1), msg.strip(), ""
        except Exception:
            pass

        # Strategy 3: GitHub REST API
        try:
            req = urllib.request.Request(
                GITHUB_COMMITS_API,
                headers={"User-Agent": "HumanizeAI-Pro-Updater", "Accept": "application/vnd.github.v3+json"},
            )
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
                if r.status == 200:
                    data = json.loads(r.read().decode("utf-8"))
                    sha = data.get("sha", "")
                    msg = data.get("commit", {}).get("message", "").splitlines()[0]
                    date = data.get("commit", {}).get("author", {}).get("date", "")
                    return sha, msg, date
        except Exception as e:
            logger.debug(f"All GitHub update checks skipped: {e}")

        return None

    def _save_cache(self, commit_sha: str):
        try:
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "current_commit": commit_sha,
                        "last_checked": time.time(),
                        "repo": GITHUB_REPO,
                    },
                    f,
                    indent=2,
                )
        except Exception as e:
            logger.debug(f"Failed saving version cache: {e}")

    def check_and_update(self, force: bool = False) -> Optional[str]:
        """Check for updates on GitHub and apply them if available.

        Args:
            force: Force check even if checked recently.

        Returns:
            Update summary string if updated, None otherwise.
        """
        # Check throttling
        if not force and os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    last_checked = data.get("last_checked", 0)
                    if (time.time() - last_checked) < CHECK_INTERVAL_SECONDS:
                        return None
            except Exception:
                pass

        logger.info(f"Checking for updates from https://github.com/{GITHUB_REPO}...")
        remote_info = self._get_remote_commit()
        if not remote_info:
            return None

        remote_sha, remote_msg, remote_date = remote_info
        local_sha = self._get_local_commit()

        # Update cache timestamp
        self._save_cache(local_sha or remote_sha)

        if local_sha and local_sha == remote_sha:
            logger.debug("Skill is already at latest GitHub version.")
            return None

        if local_sha and local_sha != remote_sha:
            logger.info(
                f"[Skill Updater] New update available on GitHub: {remote_sha[:7]} - '{remote_msg}'"
            )
            success = self._pull_updates()
            if success:
                self._sync_across_agents()
                self._save_cache(remote_sha)
                update_msg = f"Skill updated to latest GitHub version: {remote_sha[:7]} ('{remote_msg}')"
                logger.info(f"[Skill Updater] {update_msg}")
                return update_msg

        return None

    def _pull_updates(self) -> bool:
        """Pull latest changes from git repository if possible."""
        if self.repo_dir and (self.repo_dir / ".git").exists():
            try:
                logger.info(f"Pulling latest commits into {self.repo_dir}...")
                res = subprocess.run(
                    ["git", "-C", str(self.repo_dir), "pull", "origin", "main"],
                    capture_output=True,
                    text=True,
                    timeout=15,
                )
                if res.returncode == 0:
                    logger.info("Git pull succeeded.")
                    return True
                else:
                    logger.warning(f"Git pull failed: {res.stderr}")
            except Exception as e:
                logger.warning(f"Git pull execution error: {e}")

        return False

    def _sync_across_agents(self):
        """Sync updated files across all installed agent skill locations."""
        try:
            install_script = self.repo_dir / "install.py"
            if install_script.exists():
                subprocess.run(
                    [sys.executable, str(install_script)],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                logger.info("Synchronized updated skill across all agent environments.")
        except Exception as e:
            logger.debug(f"Post-update agent sync warning: {e}")
