"""
Document Stitcher for HumanizeAI.pro
Reassembles humanized chunks and preserved blocks (headers, tables, code)
into a cohesive, syntactically clean document.
"""

from typing import Dict, List
from .chunker import Chunk


class DocumentStitcher:
    """Stitches chunks back into a unified document."""

    def __init__(self):
        pass

    def stitch(self, chunks: List[Chunk], humanized_map: Dict[int, str]) -> str:
        """Reconstruct complete text from original chunks and humanized map.

        Args:
            chunks: List of Chunk objects in original order.
            humanized_map: Mapping of chunk.index to humanized text.

        Returns:
            Reassembled document string.
        """
        output_blocks = []

        for chunk in sorted(chunks, key=lambda c: c.index):
            if chunk.block_type == "header":
                # Headers are reconstructed with their original markdown prefix (#, ##, etc.)
                # If humanized text was provided for the header, use it; else original
                text = humanized_map.get(chunk.index, chunk.content)
                output_blocks.append(f"{chunk.prefix}{text.strip()}")

            elif chunk.block_type in ("code", "table", "verbatim"):
                # Code blocks, tables, and math equations are preserved verbatim
                output_blocks.append(chunk.content.rstrip())

            elif chunk.block_type == "prose":
                # Humanized prose chunk
                text = humanized_map.get(chunk.index, chunk.content)
                if chunk.prefix:
                    text = f"{chunk.prefix}{text}"
                output_blocks.append(text.strip())

            else:
                text = humanized_map.get(chunk.index, chunk.content)
                output_blocks.append(text.strip())

        # Join blocks with standard markdown paragraph separation
        assembled = "\n\n".join(b for b in output_blocks if b)
        return assembled + "\n"
