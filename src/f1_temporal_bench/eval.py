"""Run a model over the dataset and score it."""

from dataclasses import dataclass

from .dataset import Question


REFUSAL_PHRASES = [
    "i don't know", "i'm not sure", "as of my knowledge",
    "i cannot provide", "i am unable", "no information",
]


@dataclass
class EvalResult:
    total: int
    correct: int
    confidently_wrong: int
    refused: int

    @property
    def accuracy(self) -> float:
        return self.correct / self.total if self.total else 0.0

    @property
    def confidently_wrong_rate(self) -> float:
        return self.confidently_wrong / self.total if self.total else 0.0

    @property
    def refusal_rate(self) -> float:
        return self.refused / self.total if self.total else 0.0


def is_refusal(model_answer: str) -> bool:
    lower = model_answer.lower()
    return any(phrase in lower for phrase in REFUSAL_PHRASES)


def run_eval(query_fn, questions: list[Question]) -> tuple[EvalResult, list[dict]]:
    """query_fn: callable(question_text: str) -> str"""
    correct = confidently_wrong = refused = 0
    per_question = []

    for q in questions:
        model_answer = query_fn(q.question)
        refusal = is_refusal(model_answer)
        correct_flag = q.matches(model_answer)

        if correct_flag:
            correct += 1
        elif refusal:
            refused += 1
        else:
            confidently_wrong += 1

        per_question.append({
            "id": q.id,
            "question": q.question,
            "expected": q.answer,
            "model_answer": model_answer,
            "correct": correct_flag,
            "refused": refusal,
        })

    result = EvalResult(
        total=len(questions),
        correct=correct,
        confidently_wrong=confidently_wrong,
        refused=refused,
    )
    return result, per_question