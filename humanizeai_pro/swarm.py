"""
Multi-Agent Swarm Orchestrator for HumanizeAI.pro
Coordinates parallel chunk humanization, IP/proxy rotation,
rate-limit defense, stealth browser fallback, and document synthesis.
"""

import concurrent.futures
import logging
import random
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from .browser_engine import BrowserHumanizeClient
from .chunker import Chunk, SemanticChunker
from .critic import AuditResult, SemanticCritic
from .engine import HumanizeClient, HumanizeError
from .proxy_pool import ProxyPool
from .stitcher import DocumentStitcher

logger = logging.getLogger("humanizeai_pro.swarm")


@dataclass
class SwarmConfig:
    workers: int = 2
    style: str = "standard"          # Tone: Free
    writing_level: str = "advanced"  # Writing Level: Difficult (advanced)
    max_chunk_words: int = 175
    delay_between_requests: float = 0.8
    enable_jitter: bool = True
    use_browser_fallback: bool = False  # Disabled by default due to Cloudflare Turnstile hang
    proxy: Optional[str] = None
    rotate_ip: bool = True           # Enable dynamic proxy/IP rotation
    proxy_pool: Optional[ProxyPool] = None
    target_proxy_pool_size: int = 15
    audit_facts: bool = True
    strict_zero_fallback: bool = True  # Guarantee 0% silent fallback to raw unhumanized text
    max_chunk_retries: int = 6


@dataclass
class SwarmResult:
    original_text: str
    humanized_text: str
    input_word_count: int
    output_word_count: int
    chunks_total: int
    chunks_humanized: int
    elapsed_time: float
    audit: Optional[AuditResult] = None
    speed_words_per_sec: float = 0.0


class HumanizerSwarm:
    """Orchestrates multi-agent swarm processing across HumanizeAI.pro with IP rotation."""

    def __init__(self, config: Optional[SwarmConfig] = None):
        self.config = config or SwarmConfig()
        self.chunker = SemanticChunker(max_words=self.config.max_chunk_words)
        self.stitcher = DocumentStitcher()
        self.critic = SemanticCritic()
        self._browser_engine: Optional[BrowserHumanizeClient] = None

        self.proxy_pool: Optional[ProxyPool] = None
        if self.config.rotate_ip:
            self.proxy_pool = self.config.proxy_pool or ProxyPool(
                target_pool_size=self.config.target_proxy_pool_size
            )
            # Ensure we have active proxies ready
            self.proxy_pool.refresh(min_needed=3)

    def _get_browser_engine(self) -> BrowserHumanizeClient:
        if self._browser_engine is None:
            self._browser_engine = BrowserHumanizeClient()
        return self._browser_engine

    def _process_single_chunk(
        self,
        chunk: Chunk,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ) -> str:
        """Worker agent routine for processing a single chunk with proxy rotation."""
        last_exception = None

        for attempt in range(1, self.config.max_chunk_retries + 1):
            try:
                # Jitter delay to prevent burst request spikes
                if self.config.enable_jitter:
                    time.sleep(random.uniform(0.2, self.config.delay_between_requests))

                client = HumanizeClient(
                    proxy=self.config.proxy,
                    proxy_pool=self.proxy_pool,
                    rotate_ip=self.config.rotate_ip,
                    max_retries=2,
                )

                humanized = client.humanize_chunk(
                    chunk.content,
                    style=self.config.style,
                    writing_level=self.config.writing_level,
                    visible_words=200,
                )

                if humanized and humanized.strip():
                    return humanized

            except Exception as e:
                last_exception = e
                logger.warning(
                    f"[Worker Swarm] Chunk {chunk.index} attempt {attempt}/{self.config.max_chunk_retries} failed: {e}. "
                    f"Rotating proxy and retrying..."
                )
                time.sleep(random.uniform(0.5, 1.5))

        if self.config.use_browser_fallback:
            try:
                logger.info(f"[Worker Swarm] Activating stealth browser fallback for chunk {chunk.index}...")
                browser = self._get_browser_engine()
                return browser.humanize_chunk(chunk.content, style=self.config.style)
            except Exception as be:
                logger.error(f"[Worker Swarm] Stealth browser also failed: {be}")

        raise last_exception or RuntimeError(
            f"Failed to humanize chunk {chunk.index} after {self.config.max_chunk_retries} attempts."
        )

    def humanize(
        self,
        text: str,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ) -> SwarmResult:
        """Run multi-agent swarm humanization on a full document.

        Args:
            text: Full text or markdown document.
            progress_callback: Optional function(completed_chunks, total_chunks, current_stage)

        Returns:
            SwarmResult containing synthesized text, metrics, and audit report.
        """
        start_time = time.time()
        input_words = len(text.split())

        # Stage 1: Deconstruction
        if progress_callback:
            progress_callback(0, 100, "Deconstructing document into semantic chunks...")
        chunks = self.chunker.chunk_document(text)
        humanizable_chunks = [c for c in chunks if c.is_humanizable]
        total_humanizable = len(humanizable_chunks)

        logger.info(
            f"Document partitioned into {len(chunks)} total blocks ({total_humanizable} humanizable prose chunks)."
        )

        humanized_map: Dict[int, str] = {}
        completed_count = 0

        # Stage 2: Swarm Execution with Zero Fallback Guarantee
        if total_humanizable > 0:
            remaining_chunks = list(humanizable_chunks)
            pass_round = 1

            while remaining_chunks and pass_round <= 3:
                max_workers = min(self.config.workers, max(1, len(remaining_chunks)))
                next_round_failures = []

                with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                    future_to_chunk = {
                        executor.submit(self._process_single_chunk, chunk, progress_callback): chunk
                        for chunk in remaining_chunks
                    }

                    for future in concurrent.futures.as_completed(future_to_chunk):
                        chunk = future_to_chunk[future]
                        try:
                            res = future.result()
                            humanized_map[chunk.index] = res
                            completed_count += 1
                            if progress_callback:
                                progress_callback(
                                    completed_count,
                                    total_humanizable,
                                    f"Humanized chunk {completed_count}/{total_humanizable}",
                                )
                        except Exception as e:
                            logger.warning(
                                f"Pass {pass_round}: Error humanizing chunk {chunk.index}: {e}. Queueing for retry pass."
                            )
                            next_round_failures.append(chunk)

                if next_round_failures:
                    logger.warning(
                        f"Round {pass_round} ended with {len(next_round_failures)} failed chunks. Refreshing proxies..."
                    )
                    if self.proxy_pool:
                        self.proxy_pool.refresh(min_needed=5)
                    remaining_chunks = next_round_failures
                    pass_round += 1
                    time.sleep(2.0)
                else:
                    break

            # Check if any chunks failed after all passes
            if len(humanized_map) < total_humanizable:
                missing = [c.index for c in humanizable_chunks if c.index not in humanized_map]
                if self.config.strict_zero_fallback:
                    raise RuntimeError(
                        f"CRITICAL: {len(missing)} chunks failed humanization ({missing}). "
                        f"Strict zero-fallback mode prevents retaining raw AI text."
                    )
                else:
                    for c in humanizable_chunks:
                        if c.index not in humanized_map:
                            humanized_map[c.index] = c.content

        # Stage 3: Synthesis & Reassembly
        if progress_callback:
            progress_callback(total_humanizable, total_humanizable, "Reassembling document...")
        assembled_text = self.stitcher.stitch(chunks, humanized_map)

        # Stage 4: Semantic Fact Audit
        audit_res = None
        if self.config.audit_facts:
            if progress_callback:
                progress_callback(total_humanizable, total_humanizable, "Auditing citations and numerical facts...")
            audit_res = self.critic.audit(text, assembled_text)
            if audit_res.corrections_applied:
                assembled_text = audit_res.corrected_text

        elapsed = time.time() - start_time
        output_words = len(assembled_text.split())
        words_per_sec = (output_words / elapsed) if elapsed > 0 else 0.0

        return SwarmResult(
            original_text=text,
            humanized_text=assembled_text,
            input_word_count=input_words,
            output_word_count=output_words,
            chunks_total=len(chunks),
            chunks_humanized=completed_count,
            elapsed_time=elapsed,
            audit=audit_res,
            speed_words_per_sec=words_per_sec,
        )
