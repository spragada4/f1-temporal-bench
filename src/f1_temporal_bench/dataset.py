"""Load and validate the F1 temporal knowledge dataset."""

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Question:
    id: str
    date: str            # ISO date the fact became true (e.g. race date)
    question: str
    answer: str
    aliases: list[str] = field(default_factory=list)
    category: str = "general"
    season: int | None = None
    round: int | None = None

    def matches(self, model_answer: str) -> bool:
        """Case-insensitive containment match against answer + aliases."""
        candidates = [self.answer] + self.aliases
        model_answer_lower = model_answer.lower()
        return any(c.lower() in model_answer_lower for c in candidates)


def load_dataset(path: str | Path) -> list[Question]:
    path = Path(path)
    questions = []
    with path.open(encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON on line {line_num}: {e}") from e
            questions.append(Question(**row))
    return questions


def validate_dataset(path: str | Path) -> tuple[bool, list[str]]:
    """Returns (is_valid, list_of_errors)."""
    errors = []
    try:
        questions = load_dataset(path)
    except Exception as e:
        return False, [str(e)]

    seen_ids = set()
    for q in questions:
        if q.id in seen_ids:
            errors.append(f"Duplicate id: {q.id}")
        seen_ids.add(q.id)
        if not q.question.strip():
            errors.append(f"{q.id}: empty question")
        if not q.answer.strip():
            errors.append(f"{q.id}: empty answer")

    return len(errors) == 0, errors