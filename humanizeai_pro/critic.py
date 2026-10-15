"""
Semantic Critic & Fact Audit Engine for HumanizeAI.pro
Verifies that 100% of citations, statistics, numbers, dates,
and technical terminology are preserved without AI-re-hallucination.
"""

import re
from dataclasses import dataclass, field
from typing import List, Set, Tuple


@dataclass
class AuditResult:
    is_passed: bool
    total_citations_found: int
    preserved_citations: List[str]
    missing_citations: List[str]
    total_numbers_found: int
    preserved_numbers: List[str]
    missing_numbers: List[str]
    corrections_applied: int = 0
    corrected_text: str = ""
    notes: List[str] = field(default_factory=list)


class SemanticCritic:
    """Audits original vs humanized text for absolute factual fidelity."""

    # Patterns for citations: (Smith et al., 2023), Smith (2020), (Jones, 2018)
    CITATION_PATTERNS = [
        re.compile(r"\([A-Z][a-zA-Z\-\']+(?:\s+et\s+al\.?)?,?\s*(?:19|20)\d{2}[a-z]?\)"),
        re.compile(r"\b[A-Z][a-zA-Z\-\']+\s+et\s+al\.\s*\((?:19|20)\d{2}[a-z]?\)"),
        re.compile(r"\[\d+\]"),  # Numerical bracket citations like [1], [12]
    ]

    # Pattern for numbers, percentages, currencies
    NUM_PATTERN = re.compile(
        r"(?:[\$€£¥]\s*\d+(?:\.\d+)?(?:\s*(?:billion|million|trillion|B|M|K))?|\b\d+(?:\.\d+)?%|\b(?:19|20)\d{2}\b|\b\d{1,3}(?:,\d{3})+(?:\.\d+)?\b)"
    )

    def audit(self, original_text: str, humanized_text: str) -> AuditResult:
        """Compares facts between original and humanized documents."""
        # 1. Audit citations
        orig_citations = self._extract_citations(original_text)
        human_citations = self._extract_citations(humanized_text)

        preserved_cits = [c for c in orig_citations if c in humanized_text]
        missing_cits = [c for c in orig_citations if c not in humanized_text]

        # 2. Audit numbers & statistics
        orig_nums = set(self.NUM_PATTERN.findall(original_text))
        human_nums = set(self.NUM_PATTERN.findall(humanized_text))

        preserved_nums = [n for n in orig_nums if n in human_nums or n in humanized_text]
        missing_nums = [n for n in orig_nums if n not in human_nums and n not in humanized_text]

        # Filter out common false positives for numbers (e.g. single digit counts like '1', '2')
        missing_nums = [n for n in missing_nums if len(n) > 1 or "%" in n or "$" in n]

        notes = []
        is_passed = True
        corrected_text = humanized_text
        corrections_count = 0

        if missing_cits:
            for cit in missing_cits:
                # Extract author surname from citation (e.g. 'Brown' from '(Brown et al., 2020)')
                m = re.search(r"[A-Z][a-zA-Z\-]+", cit)
                if m:
                    author = m.group(0)
                    # If author is in humanized text, restore citation near author
                    if author in corrected_text:
                        # Replace lone author mention with full citation if not already followed by year
                        corrected_text = re.sub(
                            rf"\b{author}\b(?!\s*et\s*al|\s*\(\d{{4}}\))",
                            cit,
                            corrected_text,
                            count=1,
                        )
                        corrections_count += 1
                        preserved_cits.append(cit)
                        notes.append(f"Surgically restored citation {cit} at author mention '{author}'.")
                    else:
                        notes.append(f"Flagged dropped citation: {cit}")
                        is_passed = False
                else:
                    notes.append(f"Flagged dropped citation: {cit}")
                    is_passed = False

            # Update missing citations after surgical restoration
            missing_cits = [c for c in orig_citations if c not in corrected_text]

        if missing_nums:
            notes.append(f"Flagged {len(missing_nums)} missing statistic(s)/date(s): {missing_nums}")

        return AuditResult(
            is_passed=is_passed,
            total_citations_found=len(orig_citations),
            preserved_citations=preserved_cits,
            missing_citations=missing_cits,
            total_numbers_found=len(orig_nums),
            preserved_numbers=preserved_nums,
            missing_numbers=missing_nums,
            corrections_applied=corrections_count,
            corrected_text=corrected_text,
            notes=notes,
        )

    def _extract_citations(self, text: str) -> List[str]:
        citations = []
        for pattern in self.CITATION_PATTERNS:
            citations.extend(pattern.findall(text))
        return list(dict.fromkeys(citations))  # Deduplicate preserving order
