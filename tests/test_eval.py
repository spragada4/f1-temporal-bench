from f1_temporal_bench.dataset import Question
from f1_temporal_bench.eval import is_refusal, run_eval


def test_question_matches():
    q = Question(id="t1", date="2024-01-01", question="Who won?", answer="Max Verstappen", aliases=["Verstappen"])
    assert q.matches("The winner was Max Verstappen.")
    assert q.matches("It was Verstappen.")
    assert not q.matches("Lewis Hamilton won.")


def test_is_refusal():
    assert is_refusal("I don't know the answer to that.")
    assert not is_refusal("Max Verstappen")


def test_run_eval_scores_correctly():
    questions = [
        Question(id="t1", date="2024-01-01", question="Q1", answer="Alpha"),
        Question(id="t2", date="2024-01-01", question="Q2", answer="Beta"),
    ]

    fake_answers = {"Q1": "Alpha", "Q2": "I'm not sure"}
    result, _ = run_eval(lambda q: fake_answers[q], questions)

    assert result.total == 2
    assert result.correct == 1
    assert result.refused == 1
    assert result.confidently_wrong == 0