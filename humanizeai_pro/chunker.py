"""
Semantic Chunker for HumanizeAI.pro
Splits arbitrary-length documents into safe semantic units (<= 170 words)
preserving markdown formatting, headings, code blocks, tables, and lists.
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Chunk:
    index: int
    content: str
    block_type: str = "prose"  # 'prose', 'header', 'code', 'table', 'verbatim'
    prefix: str = ""
    metadata: dict = field(default_factory=dict)

    @property
    def word_count(self) -> int:
        return len(self.content.split())

    @property
    def is_humanizable(self) -> bool:
        return self.block_type == "prose" and self.word_count > 0


class SemanticChunker:
    """Intelligently chunks documents into humanizable segments of <= max_words."""

    def __init__(self, target_words: int = 150, max_words: int = 180):
        self.target_words = target_words
        self.max_words = max_words

    def chunk_document(self, text: str) -> List[Chunk]:
        """Parse full document and return list of ordered Chunks."""
        lines = text.splitlines(keepends=True)
        raw_blocks = self._parse_blocks(lines)
        chunks: List[Chunk] = []
        chunk_idx = 0

        for block_type, content, prefix in raw_blocks:
            if block_type != "prose":
                chunks.append(
                    Chunk(
                        index=chunk_idx,
                        content=content,
                        block_type=block_type,
                        prefix=prefix,
                    )
                )
                chunk_idx += 1
            else:
                # Prose block: if within limit, keep as single chunk; else split on sentences
                words = content.split()
                if len(words) <= self.max_words:
                    chunks.append(
                        Chunk(
                            index=chunk_idx,
                            content=content.strip(),
                            block_type="prose",
                            prefix=prefix,
                        )
                    )
                    chunk_idx += 1
                else:
                    sub_chunks = self._split_prose_sentences(content, prefix, chunk_idx)
                    for sc in sub_chunks:
                        chunks.append(sc)
                        chunk_idx += 1

        return chunks

    def _parse_blocks(self, lines: List[str]) -> List[tuple]:
        """Separates text into code blocks, tables, headers, and prose paragraphs."""
        blocks = []
        in_code_block = False
        code_buffer = []
        code_fence = ""

        prose_buffer = []

        def flush_prose():
            if prose_buffer:
                p_text = "".join(prose_buffer).strip()
                if p_text:
                    blocks.append(("prose", p_text, ""))
                prose_buffer.clear()

        i = 0
        while i < len(lines):
            line = lines[i]

            # Code fence detection (``` or ~~~)
            code_match = re.match(r"^(\s*)(`{3,}|~{3,})", line)
            if code_match:
                if not in_code_block:
                    flush_prose()
                    in_code_block = True
                    code_fence = code_match.group(2)
                    code_buffer = [line]
                else:
                    code_buffer.append(line)
                    if code_match.group(2) == code_fence:
                        blocks.append(("code", "".join(code_buffer), ""))
                        in_code_block = False
                        code_buffer = []
                i += 1
                continue

            if in_code_block:
                code_buffer.append(line)
                i += 1
                continue

            # Markdown header detection (# Header)
            header_match = re.match(r"^(#{1,6}\s+)(.+)$", line.strip())
            if header_match:
                flush_prose()
                prefix = header_match.group(1)
                header_text = header_match.group(2)
                blocks.append(("header", header_text, prefix))
                i += 1
                continue

            # Table detection (| col | col |)
            if line.strip().startswith("|") and line.strip().endswith("|"):
                flush_prose()
                table_lines = [line]
                i += 1
                while i < len(lines) and lines[i].strip().startswith("|") and lines[i].strip().endswith("|"):
                    table_lines.append(lines[i])
                    i += 1
                blocks.append(("table", "".join(table_lines), ""))
                continue

            # LaTeX math block detection ($$ ... $$)
            if line.strip().startswith("$$"):
                flush_prose()
                math_lines = [line]
                if not line.strip().endswith("$$") or line.strip() == "$$":
                    i += 1
                    while i < len(lines):
                        math_lines.append(lines[i])
                        if lines[i].strip().endswith("$$"):
                            i += 1
                            break
                        i += 1
                else:
                    i += 1
                blocks.append(("verbatim", "".join(math_lines), ""))
                continue

            # Blank line / paragraph separator
            if not line.strip():
                flush_prose()
                i += 1
                continue

            prose_buffer.append(line)
            i += 1

        flush_prose()
        return blocks

    def _split_prose_sentences(self, text: str, prefix: str, start_index: int) -> List[Chunk]:
        """Splits large prose paragraphs into sentence-boundary chunks <= max_words."""
        # Split on sentence boundaries preserving delimiters
        sentence_endings = re.compile(r"([.?!]+(?:\s+|$))")
        tokens = sentence_endings.split(text)

        sentences = []
        for j in range(0, len(tokens) - 1, 2):
            sentences.append(tokens[j] + tokens[j + 1])
        if len(tokens) % 2 == 1 and tokens[-1].strip():
            sentences.append(tokens[-1])

        chunks = []
        current_sentences = []
        current_word_count = 0

        for sentence in sentences:
            s_words = len(sentence.split())
            if current_word_count + s_words > self.max_words and current_sentences:
                chunk_str = "".join(current_sentences).strip()
                chunks.append(
                    Chunk(
                        index=start_index + len(chunks),
                        content=chunk_str,
                        block_type="prose",
                        prefix=prefix,
                    )
                )
                current_sentences = [sentence]
                current_word_count = s_words
            else:
                current_sentences.append(sentence)
                current_word_count += s_words

        if current_sentences:
            chunk_str = "".join(current_sentences).strip()
            chunks.append(
                Chunk(
                    index=start_index + len(chunks),
                    content=chunk_str,
                    block_type="prose",
                    prefix=prefix,
                )
            )

        return chunks
