"""
Core HTTP Engine for HumanizeAI.pro
Handles resilient communication, antibot bypass, header rotation,
session lifecycle, IP rotation, and error recovery.
"""

import json
import logging
import random
import ssl
import time
import urllib.error
import urllib.request
import uuid
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("humanizeai_pro.engine")

VALID_STYLES = [
    "standard",
    "academic",
    "simple",
    "flowing",
    "informal",
    "formal",
    "expand",
    "shorten",
]

VALID_WRITING_LEVELS = [
    "academic",  # Very difficult (Default - Highest human authenticity score on Turnitin)
    "advanced",  # Fairly difficult
    "standard",  # Fairly easy
    "simple",    # Easy to read
]

WRITING_LEVEL_ALIASES = {
    "very-difficult": "academic",
    "very_difficult": "academic",
    "very difficult": "academic",
    "difficult": "academic",
    "academic": "academic",
    "fairly-difficult": "advanced",
    "fairly_difficult": "advanced",
    "fairly difficult": "advanced",
    "advanced": "advanced",
    "fairly-easy": "standard",
    "fairly_easy": "standard",
    "fairly easy": "standard",
    "standard": "standard",
    "easy-to-read": "simple",
    "easy_to_read": "simple",
    "simple": "simple",
}

USER_AGENTS = [
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        '"Windows"',
    ),
    (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        '"macOS"',
    ),
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
        '"Microsoft Edge";v="123", "Chromium";v="123", "Not-A.Brand";v="99"',
        '"Windows"',
    ),
    (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        '"Linux"',
    ),
]


class HumanizeError(Exception):
    """Base exception for humanize client errors."""

    def __init__(self, message: str, status_code: Optional[int] = None, response_body: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class HumanizeClient:
    """Direct HTTP Client for https://www.humanizeai.pro/api/process

    Implements realistic browser fingerprints, dynamic session tracking,
    anti-bot evasion tokens, proxy/IP rotation, and adaptive backoff retry logic.
    """

    API_ENDPOINT = "https://www.humanizeai.pro/api/process"
    HOME_URL = "https://www.humanizeai.pro/"

    def __init__(
        self,
        max_retries: int = 5,
        base_delay: float = 1.0,
        max_delay: float = 8.0,
        enable_jitter: bool = True,
        proxy: Optional[str] = None,
        proxy_pool: Optional[Any] = None,
        rotate_ip: bool = False,
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.enable_jitter = enable_jitter
        self.proxy = proxy
        self.proxy_pool = proxy_pool
        self.rotate_ip = rotate_ip

        if self.rotate_ip and self.proxy_pool is None:
            try:
                from .proxy_pool import ProxyPool
                self.proxy_pool = ProxyPool()
                self.proxy_pool.refresh(min_needed=3)
            except Exception as e:
                logger.warning(f"Could not initialize ProxyPool: {e}")

        self.session_id = str(uuid.uuid4())
        self._ua_tuple = random.choice(USER_AGENTS)

    def _rotate_identity(self):
        """Rotate session ID and browser fingerprint."""
        self.session_id = str(uuid.uuid4())
        self._ua_tuple = random.choice(USER_AGENTS)

    def _get_headers(self) -> Dict[str, str]:
        ua, sec_ch_ua, sec_platform = self._ua_tuple
        headers = {
            "User-Agent": ua,
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Content-Type": "application/json",
            "Origin": "https://www.humanizeai.pro",
            "Referer": "https://www.humanizeai.pro/",
            "Sec-Ch-Ua": sec_ch_ua,
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": sec_platform,
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }
        return headers

    def humanize_chunk(
        self,
        text: str,
        style: str = "standard",
        writing_level: str = "academic",
        visible_words: int = 200,
        timeout: float = 35.0,
    ) -> str:
        """Humanize a single text chunk using Writing Level Very difficult (academic) and Tone Free.

        Args:
            text: Input text chunk to humanize.
            style: Tone style ('standard' represents Tone 'Free').
            writing_level: Writing level ('academic' represents 'Very difficult',
                           'advanced' represents 'Fairly difficult', 'standard', 'simple').
            visible_words: Words visible limit (default 200).
            timeout: Request timeout in seconds.

        Returns:
            Humanized text string.
        """
        cleaned = text.strip()
        if not cleaned:
            return ""

        if style not in VALID_STYLES:
            style = "standard"

        # Resolve aliases like 'very-difficult', 'difficult' -> 'academic'
        norm_level = WRITING_LEVEL_ALIASES.get(writing_level.lower().strip(), writing_level)
        if norm_level not in VALID_WRITING_LEVELS:
            norm_level = "academic"

        payload = {
            "text": cleaned,
            "trialNumber": 0,
            "alg": 0,
            "keywords": [],
            "sessionId": self.session_id,
            "style": style,
            "isLogged": False,
            "ultra": False,
            "from_detector": True,
            "turnstileToken": "turnstile-bypass",
            "visibleWords": visible_words,
            "writingLevel": norm_level,
        }

        data_bytes = json.dumps(payload).encode("utf-8")
        last_error = None

        ssl_ctx = ssl._create_unverified_context()

        for attempt in range(1, self.max_retries + 1):
            active_proxy = None
            if self.proxy_pool:
                active_proxy = self.proxy_pool.get_proxy()
            elif self.proxy:
                active_proxy = self.proxy

            try:
                headers = self._get_headers()
                req = urllib.request.Request(self.API_ENDPOINT, data=data_bytes, headers=headers)

                if active_proxy:
                    proxy_url = f"http://{active_proxy}" if not active_proxy.startswith("http") else active_proxy
                    proxy_handler = urllib.request.ProxyHandler({"http": proxy_url, "https": proxy_url})
                    opener = urllib.request.build_opener(proxy_handler, urllib.request.HTTPSHandler(context=ssl_ctx))
                else:
                    opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ssl_ctx))

                with opener.open(req, timeout=timeout) as resp:
                    status_code = resp.status
                    raw_body = resp.read().decode("utf-8", errors="ignore")
                    res_json = json.loads(raw_body)

                    results = res_json.get("result", [])
                    if results and isinstance(results, list):
                        humanized_text = results[0].get("text", "").strip()
                        if humanized_text:
                            # Acknowledge proxy success if using pool
                            if self.proxy_pool and active_proxy:
                                self.proxy_pool.report_success(active_proxy)
                            return humanized_text

                    # If result text is empty but locked exists, warn about word count
                    if "locked" in res_json and not (results and results[0].get("text")):
                        locked_info = res_json.get("locked", {})
                        logger.warning(
                            f"Chunk word count exceeded free boundary: {locked_info}. Retrying with fresh session..."
                        )

            except urllib.error.HTTPError as e:
                body = e.read().decode("utf-8", errors="ignore") if e.fp else ""
                last_error = HumanizeError(f"HTTP {e.code}: {e.reason}", status_code=e.code, response_body=body)
                logger.warning(
                    f"Attempt {attempt}/{self.max_retries} failed on proxy {active_proxy}: HTTP {e.code} - {body}"
                )

                if self.proxy_pool and active_proxy:
                    self.proxy_pool.report_failure(active_proxy)

                if e.code in (403, 429):
                    # Rate limit or antibot: rotate identity and backoff
                    self._rotate_identity()

            except Exception as e:
                last_error = HumanizeError(f"Network error on proxy {active_proxy}: {str(e)}")
                logger.warning(f"Attempt {attempt}/{self.max_retries} connection failed on proxy {active_proxy}: {e}")
                if self.proxy_pool and active_proxy:
                    self.proxy_pool.report_failure(active_proxy)
                self._rotate_identity()

            if attempt < self.max_retries:
                # Exponential backoff with jitter
                delay = min(self.max_delay, self.base_delay * (2 ** (attempt - 1)))
                if self.enable_jitter:
                    delay += random.uniform(0.3, 1.2)
                time.sleep(delay)

        raise last_error or HumanizeError("Exhausted all retries without successful response.")
