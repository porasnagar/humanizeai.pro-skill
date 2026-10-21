"""
HumanizeAI Pro Swarm Engine & Agent Skill
Multi-agent swarm for humanizing arbitrary-length documents via humanizeai.pro
with built-in anti-bot bypass, adaptive rate-limiting, dynamic proxy IP rotation,
and lossless reassembly.
"""

__version__ = "1.1.0"

from .engine import HumanizeClient, HumanizeError
from .chunker import SemanticChunker, Chunk
from .stitcher import DocumentStitcher
from .swarm import HumanizerSwarm, SwarmConfig
from .critic import SemanticCritic, AuditResult
from .extractor import DocumentExtractor
from .formatter import DocumentFormatter
from .proxy_pool import ProxyPool

__all__ = [
    "HumanizeClient",
    "HumanizeError",
    "SemanticChunker",
    "Chunk",
    "DocumentStitcher",
    "HumanizerSwarm",
    "SwarmConfig",
    "SemanticCritic",
    "AuditResult",
    "DocumentExtractor",
    "DocumentFormatter",
    "ProxyPool",
]
