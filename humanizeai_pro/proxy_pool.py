"""
Dynamic Proxy Pool & IP Rotation Engine for HumanizeAI.pro
Fetches, validates, and rotates live proxies to bypass Cloudflare Error 1015,
IP rate limits, and regional blocks.
"""

import concurrent.futures
import json
import logging
import os
import random
import threading
import time
import urllib.request
import urllib.error
from typing import List, Optional, Set

logger = logging.getLogger("humanizeai_pro.proxy_pool")

PUBLIC_SOURCES = [
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=5000&country=all&ssl=all&anonymity=all",
]

TEST_PAYLOAD = json.dumps({
    "text": "Automated machine learning simplifies complex AI model selection and hyperparameter optimization.",
    "trialNumber": 0,
    "alg": 0,
    "keywords": [],
    "sessionId": "proxy-test-init",
    "style": "standard",
    "isLogged": False,
    "ultra": False,
    "from_detector": True,
    "turnstileToken": "turnstile-bypass",
    "visibleWords": 200,
    "writingLevel": "advanced",
}).encode("utf-8")

TEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Origin": "https://www.humanizeai.pro",
    "Referer": "https://www.humanizeai.pro/",
}


class ProxyPool:
    """Manages dynamic proxy validation and IP rotation for HumanizeClient."""

    def __init__(self, cache_file: Optional[str] = None, target_pool_size: int = 15):
        self.target_pool_size = target_pool_size
        self.cache_file = cache_file or os.path.join(
            os.path.expanduser("~"), ".humanizeai_proxies.json"
        )
        self.verified_proxies: List[str] = []
        self.failed_proxies: Set[str] = set()
        self.lock = threading.Lock()
        self.current_idx = 0

        # Load cached proxies if available
        self._load_cache()

    def _load_cache(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.verified_proxies = [p for p in data if isinstance(p, str)]
                        logger.info(f"Loaded {len(self.verified_proxies)} cached proxies.")
            except Exception as e:
                logger.warning(f"Failed loading proxy cache: {e}")

    def _save_cache(self):
        try:
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self.verified_proxies, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed saving proxy cache: {e}")

    def fetch_candidate_proxies(self) -> List[str]:
        """Fetch raw candidate proxies from public endpoints."""
        candidates = set()
        for url in PUBLIC_SOURCES:
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=8) as r:
                    content = r.read().decode("utf-8", errors="ignore")
                    for line in content.splitlines():
                        line = line.strip()
                        if line and ":" in line and not line.startswith("#"):
                            candidates.add(line)
            except Exception as e:
                logger.debug(f"Source {url} fetch error: {e}")

        # Exclude known failures
        with self.lock:
            active_set = set(self.verified_proxies)
            candidates = candidates - self.failed_proxies - active_set

        candidate_list = list(candidates)
        random.shuffle(candidate_list)
        return candidate_list

    @staticmethod
    def test_proxy(proxy: str, timeout: float = 6.0) -> bool:
        """Validate if a proxy can successfully reach HumanizeAI.pro and return 200 OK."""
        proxy_url = f"http://{proxy}" if not proxy.startswith("http") else proxy
        proxy_handler = urllib.request.ProxyHandler({"http": proxy_url, "https": proxy_url})
        opener = urllib.request.build_opener(proxy_handler)
        req = urllib.request.Request(
            "https://www.humanizeai.pro/api/process",
            data=TEST_PAYLOAD,
            headers=TEST_HEADERS,
        )
        try:
            with opener.open(req, timeout=timeout) as resp:
                if resp.status == 200:
                    raw = resp.read().decode("utf-8", errors="ignore")
                    data = json.loads(raw)
                    results = data.get("result", [])
                    if results and isinstance(results, list) and results[0].get("text"):
                        return True
        except Exception:
            pass
        return False

    def refresh(self, min_needed: int = 5, max_candidates_to_test: int = 150):
        """Find working proxies until pool size reaches min_needed."""
        with self.lock:
            if len(self.verified_proxies) >= min_needed:
                return

        candidates = self.fetch_candidate_proxies()
        logger.info(f"Testing up to {min(len(candidates), max_candidates_to_test)} proxies against HumanizeAI API...")

        found = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
            futures = {
                executor.submit(self.test_proxy, p): p
                for p in candidates[:max_candidates_to_test]
            }
            for fut in concurrent.futures.as_completed(futures):
                p = futures[fut]
                try:
                    if fut.result():
                        logger.info(f"Verified working proxy: {p}")
                        found.append(p)
                        with self.lock:
                            if p not in self.verified_proxies:
                                self.verified_proxies.append(p)
                                self._save_cache()
                        if len(self.verified_proxies) >= self.target_pool_size:
                            break
                except Exception:
                    with self.lock:
                        self.failed_proxies.add(p)

        logger.info(f"Proxy pool refreshed. Total active verified proxies: {len(self.verified_proxies)}")

    def get_proxy(self) -> Optional[str]:
        """Get the next working proxy in rotation."""
        with self.lock:
            if not self.verified_proxies:
                return None
            proxy = self.verified_proxies[self.current_idx % len(self.verified_proxies)]
            self.current_idx += 1
            return proxy

    def report_failure(self, proxy: str):
        """Mark a proxy as dead or rate-limited and remove it."""
        with self.lock:
            if proxy in self.verified_proxies:
                self.verified_proxies.remove(proxy)
                self.failed_proxies.add(proxy)
                self._save_cache()
                logger.warning(f"Removed dead proxy: {proxy}. Remaining: {len(self.verified_proxies)}")

        # Trigger auto-refresh if pool is running low
        if len(self.verified_proxies) < 3:
            threading.Thread(target=self.refresh, kwargs={"min_needed": 5}, daemon=True).start()

    def report_success(self, proxy: str):
        """Acknowledge proxy success (re-confirms health)."""
        with self.lock:
            if proxy not in self.verified_proxies:
                self.verified_proxies.append(proxy)
                self._save_cache()

    def __len__(self):
        with self.lock:
            return len(self.verified_proxies)
