"""Token optimization service for PromptForge.

Inspired by the 'caveman' project (83.8k stars) which reduces token usage
by simplifying language, and 'ponytail' which teaches agents to be concise.
This service provides multiple optimization strategies.
"""
import re

try:
    import tiktoken
    _ENCODER = tiktoken.get_encoding("cl100k_base")
except Exception:
    _ENCODER = None


class TokenOptimizer:
    """Optimize prompts to reduce token usage while preserving meaning."""

    # Redundant phrases that can be simplified
    REDUNDANCY_MAP = {
        "in order to": "to",
        "due to the fact that": "because",
        "in the event that": "if",
        "at this point in time": "now",
        "in the process of": "",
        "it should be noted that": "",
        "it is important to note that": "",
        "please note that": "",
        "it is worth noting that": "",
        "needless to say": "",
        "for all intents and purposes": "",
        "in terms of": "for",
        "with regard to": "about",
        "in accordance with": "per",
        "prior to": "before",
        "subsequent to": "after",
        "a large number of": "many",
        "a majority of": "most",
        "the vast majority of": "most",
        "has the ability to": "can",
        "is able to": "can",
        "are able to": "can",
        "has the potential to": "could",
        "make a decision": "decide",
        "take into consideration": "consider",
        "come to a conclusion": "conclude",
        "perform an analysis": "analyze",
        "conduct an investigation": "investigate",
        "give consideration to": "consider",
        "make an assessment": "assess",
        "provide a description": "describe",
        "carry out": "do",
        "put forward": "propose",
        "bring about": "cause",
        "in the near future": "soon",
        "at the present time": "now",
        "in the not too distant future": "soon",
    }

    # Filler words that add no value
    FILLER_PATTERNS = [
        r"\bbasically\b",
        r"\bactually\b",
        r"\bsimply\b",
        r"\breally\b",
        r"\bvery\b",
        r"\bquite\b",
        r"\bjust\b(?!\s+do)",
        r"\bliterally\b",
        r"\bsort of\b",
        r"\bkind of\b",
        r"\byou know\b",
        r"\bi mean\b",
        r"\bin other words\b",
        r"\bthat is to say\b",
        r"\bas a matter of fact\b",
    ]

    def __init__(self):
        self.encoder = _ENCODER

    def count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken, with fallback approximation."""
        if self.encoder:
            return len(self.encoder.encode(text))
        # Fallback: approximate ~1.3 tokens per word for English, ~2 for CJK
        words = len(text.split())
        cjk_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        return int(words * 1.3 + cjk_chars * 0.5)

    def _remove_redundancy(self, text: str) -> str:
        """Replace verbose phrases with concise alternatives."""
        for verbose, concise in self.REDUNDANCY_MAP.items():
            text = re.sub(re.escape(verbose), concise, text, flags=re.IGNORECASE)
        return text

    def _remove_fillers(self, text: str) -> str:
        """Remove filler words that add no semantic value."""
        for pattern in self.FILLER_PATTERNS:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE)
        return text

    def _collapse_whitespace(self, text: str) -> str:
        """Collapse multiple whitespace into single space, preserve newlines."""
        lines = text.split("\n")
        cleaned_lines = []
        for line in lines:
            line = re.sub(r"[ \t]+", " ", line).strip()
            cleaned_lines.append(line)
        # Remove consecutive empty lines
        result = []
        prev_empty = False
        for line in cleaned_lines:
            if line == "":
                if not prev_empty:
                    result.append(line)
                prev_empty = True
            else:
                result.append(line)
                prev_empty = False
        return "\n".join(result).strip()

    def _merge_sentences(self, text: str) -> str:
        """Merge short fragmented sentences into compound sentences."""
        sentences = re.split(r"(?<=[.!?])\s+", text)
        if len(sentences) <= 1:
            return text
        merged = []
        i = 0
        while i < len(sentences):
            current = sentences[i].strip()
            # Try to merge with next sentence if both are short
            if i + 1 < len(sentences):
                next_sent = sentences[i + 1].strip()
                if len(current.split()) < 8 and len(next_sent.split()) < 8:
                    # Merge using semicolon or conjunction
                    if next_sent.lower().startswith(("and ", "but ", "so ", "or ")):
                        merged.append(f"{current} {next_sent}")
                    else:
                        merged.append(f"{current}; {next_sent}")
                    i += 2
                    continue
            merged.append(current)
            i += 1
        return ". ".join(merged) if "." not in text else " ".join(merged)

    def _compress_instructions(self, text: str) -> str:
        """Compress repetitive instruction patterns."""
        # Replace "You should X. You should Y." with "X and Y."
        text = re.sub(r"(You should|You must|You need to|Please)\s+", "", text, flags=re.IGNORECASE)
        # Replace "Do not X. Do not Y." patterns
        text = re.sub(r"Do not\s+", "Don't ", text, flags=re.IGNORECASE)
        return text

    def optimize(self, content: str, strategy: str = "balanced") -> dict:
        """
        Optimize prompt content to reduce tokens.

        Strategies:
        - minimal: only remove redundancy and fillers
        - balanced: minimal + whitespace + instruction compression
        - aggressive: balanced + sentence merging + deeper compression
        """
        original_tokens = self.count_tokens(content)
        optimized = content

        # Step 1: Always remove redundancy and fillers
        optimized = self._remove_redundancy(optimized)
        optimized = self._remove_fillers(optimized)

        if strategy in ("balanced", "aggressive"):
            optimized = self._compress_instructions(optimized)
            optimized = self._collapse_whitespace(optimized)

        if strategy == "aggressive":
            optimized = self._merge_sentences(optimized)
            # Remove articles where context is clear
            optimized = re.sub(r"\b(the|a|an)\b (?=\w+ (is|are|will|should|must|can))",
                             "", optimized, flags=re.IGNORECASE)
            optimized = self._collapse_whitespace(optimized)

        optimized_tokens = self.count_tokens(optimized)
        reduction_pct = round(
            ((original_tokens - optimized_tokens) / max(original_tokens, 1)) * 100, 1
        )

        return {
            "original_content": content,
            "optimized_content": optimized,
            "original_tokens": original_tokens,
            "optimized_tokens": optimized_tokens,
            "reduction_pct": reduction_pct,
            "strategy": strategy,
        }


optimizer = TokenOptimizer()
