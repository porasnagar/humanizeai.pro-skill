import os
import sys
import unittest
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from humanizeai_pro.chunker import SemanticChunker, Chunk
from humanizeai_pro.stitcher import DocumentStitcher
from humanizeai_pro.critic import SemanticCritic
from humanizeai_pro.formatter import DocumentFormatter
from humanizeai_pro.extractor import DocumentExtractor



class TestHumanizeAIPro(unittest.TestCase):

    def test_chunker_preserves_structure(self):
        doc = (
            "# Main Title\n\n"
            "This is a prose paragraph discussing machine learning paradigms.\n\n"
            "```python\n"
            "def foo():\n"
            "    return True\n"
            "```\n\n"
            "| Col A | Col B |\n"
            "| --- | --- |\n"
            "| 1 | 2 |\n\n"
            "## Section 2\n\n"
            "Final concluding paragraph with citations (Smith et al., 2023)."
        )
        chunker = SemanticChunker(max_words=175)
        chunks = chunker.chunk_document(doc)

        block_types = [c.block_type for c in chunks]
        self.assertIn("header", block_types)
        self.assertIn("code", block_types)
        self.assertIn("table", block_types)
        self.assertIn("prose", block_types)

        # Ensure all chunks are <= 180 words
        for c in chunks:
            self.assertLessEqual(c.word_count, 180)

    def test_stitcher_lossless_reassembly(self):
        doc = "# Title\n\nFirst paragraph.\n\n```python\nprint('code')\n```\n\nSecond paragraph."
        chunker = SemanticChunker(max_words=175)
        chunks = chunker.chunk_document(doc)

        # Dummy humanized map
        h_map = {c.index: c.content.upper() for c in chunks if c.block_type == "prose"}

        stitcher = DocumentStitcher()
        assembled = stitcher.stitch(chunks, h_map)

        self.assertIn("# Title", assembled)
        self.assertIn("print('code')", assembled)
        self.assertIn("FIRST PARAGRAPH.", assembled)

    def test_critic_citation_and_number_audit(self):
        original = "According to Vaswani et al. (2017), transformer architectures achieved 98.4% retention in 2024."
        humanized = "As reported by Vaswani et al. (2017), transformer networks reached 98.4% performance in 2024."

        critic = SemanticCritic()
        audit = critic.audit(original, humanized)

        self.assertTrue(audit.is_passed)
        self.assertIn("Vaswani et al. (2017)", audit.preserved_citations)
        self.assertIn("98.4%", audit.preserved_numbers)
        self.assertEqual(len(audit.missing_citations), 0)

    def test_formatter_exports(self):
        sample = "# Testing Document\n\nThis is a sample document for testing formatting engines."
        tmp_dir = Path("tests/tmp_exports")
        tmp_dir.mkdir(parents=True, exist_ok=True)

        md_path = DocumentFormatter.export(sample, str(tmp_dir / "test.md"), "md")
        self.assertTrue(Path(md_path).exists())

        docx_path = DocumentFormatter.export(sample, str(tmp_dir / "test.docx"), "docx")
        self.assertTrue(Path(docx_path).exists())

        pdf_path = DocumentFormatter.export(sample, str(tmp_dir / "test.pdf"), "pdf")
        self.assertTrue(Path(pdf_path).exists())

        tex_path = DocumentFormatter.export(sample, str(tmp_dir / "test.tex"), "latex")
        self.assertTrue(Path(tex_path).exists())


if __name__ == "__main__":
    unittest.main()
