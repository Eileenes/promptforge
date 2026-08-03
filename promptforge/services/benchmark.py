"""Benchmarking service for PromptForge.

Scores prompts based on clarity, specificity, and structure.
Inspired by ARC-AGI and lmms-eval evaluation approaches.
"""
import re
from services.optimizer import optimizer


class PromptBenchmark:
    """Benchmark and score prompts on multiple dimensions."""

    def score_clarity(self, text: str) -> float:
        """Score clarity based on sentence length and structure (0-10)."""
        sentences = [s for s in re.split(r"[.!?]+", text) if s.strip()]
        if not sentences:
            return 5.0
        avg_len = sum(len(s.split()) for s in sentences) / len(sentences)
        # Ideal sentence length: 10-20 words
        if avg_len <= 20:
            return 10.0 - (avg_len - 10) * 0.2 if avg_len >= 10 else avg_len * 0.5 + 5.0
        else:
            return max(2.0, 10.0 - (avg_len - 20) * 0.3)

    def score_specificity(self, text: str) -> float:
        """Score specificity based on concrete details and constraints (0-10)."""
        score = 5.0
        # Check for specific constraints
        constraint_patterns = [
            (r"\d+", 0.5),  # Numbers
            (r"\b(must|should|required|need to)\b", 0.3),  # Requirements
            (r"\b(format|structure|style|tone)\b", 0.4),  # Format specs
            (r"\b(example|examples|e\.g\.|i\.e\.)\b", 0.4),  # Examples
            (r"\b(step|steps|first|second|third|finally)\b", 0.3),  # Structure
            (r"\b(do not|don't|avoid|never)\b", 0.3),  # Negative constraints
            (r"\b(JSON|markdown|table|list|bullet)\b", 0.4),  # Output format
        ]
        for pattern, bonus in constraint_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                score += bonus
        return min(10.0, score)

    def score_structure(self, text: str) -> float:
        """Score structural organization (0-10)."""
        score = 3.0
        # Check for structural elements
        if re.search(r"^#{1,6}\s", text, re.MULTILINE):  # Markdown headers
            score += 2.0
        if re.search(r"^\d+\.\s", text, re.MULTILINE):  # Numbered lists
            score += 1.5
        if re.search(r"^[-*]\s", text, re.MULTILINE):  # Bullet lists
            score += 1.5
        if re.search(r"```", text):  # Code blocks
            score += 1.0
        if "\n\n" in text:  # Paragraph breaks
            score += 1.0
        return min(10.0, score)

    def score_token_efficiency(self, text: str) -> float:
        """Score token efficiency - lower tokens for same meaning is better (0-10)."""
        tokens = optimizer.count_tokens(text)
        if tokens == 0:
            return 0.0
        # Optimal range: 50-200 tokens for most prompts
        if tokens <= 50:
            return 10.0
        elif tokens <= 200:
            return 10.0 - (tokens - 50) * 0.02
        elif tokens <= 500:
            return 7.0 - (tokens - 200) * 0.005
        else:
            return max(2.0, 5.5 - (tokens - 500) * 0.005)

    def benchmark(self, content: str) -> dict:
        """Run full benchmark on a prompt."""
        clarity = round(self.score_clarity(content), 1)
        specificity = round(self.score_specificity(content), 1)
        structure = round(self.score_structure(content), 1)
        efficiency = round(self.score_token_efficiency(content), 1)
        overall = round((clarity + specificity + structure + efficiency) / 4, 1)
        token_count = optimizer.count_tokens(content)

        return {
            "clarity": clarity,
            "specificity": specificity,
            "structure": structure,
            "token_efficiency": efficiency,
            "overall_score": overall,
            "token_count": token_count,
            "suggestions": self._generate_suggestions(
                clarity, specificity, structure, efficiency
            ),
        }

    def _generate_suggestions(self, clarity, specificity, structure, efficiency) -> list:
        """Generate improvement suggestions based on scores."""
        suggestions = []
        if clarity < 7:
            suggestions.append("Consider using shorter, more direct sentences")
        if specificity < 7:
            suggestions.append("Add more concrete constraints, examples, and format specifications")
        if structure < 7:
            suggestions.append("Use markdown headers, numbered lists, or bullet points to organize")
        if efficiency < 7:
            suggestions.append("Run the optimizer to reduce token usage without losing meaning")
        if not suggestions:
            suggestions.append("Great prompt! All dimensions score well")
        return suggestions


benchmark = PromptBenchmark()
