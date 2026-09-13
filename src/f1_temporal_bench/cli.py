"""Command-line interface: f1-temporal-bench"""

import json
import sys

import click
from rich.console import Console
from rich.table import Table

from .dataset import load_dataset, validate_dataset
from .eval import run_eval
from .models import query_hf_inference, query_local_model

console = Console()


@click.group()
def main():
    """F1 Temporal Knowledge Benchmark CLI."""
    pass


@main.command()
@click.option("--path", default="data/questions.jsonl", help="Path to dataset.")
def validate(path):
    """Validate the dataset file for schema errors."""
    ok, errors = validate_dataset(path)
    if ok:
        console.print(f"[green]Dataset valid: {path}[/green]")
    else:
        console.print(f"[red]{len(errors)} error(s) found:[/red]")
        for e in errors:
            console.print(f"  - {e}")
        sys.exit(1)


@main.command()
@click.option("--model", required=True, help="HF model id, e.g. meta-llama/Llama-3.2-1B-Instruct")
@click.option("--dataset", default="data/questions.jsonl", help="Path to dataset.")
@click.option("--local", is_flag=True, help="Run the model locally instead of via HF Inference API.")
@click.option("--output", default=None, help="Optional path to write JSON results.")
def run(model, dataset, local, output):
    """Evaluate a model against the dataset."""
    questions = load_dataset(dataset)
    console.print(f"Loaded {len(questions)} questions. Evaluating [bold]{model}[/bold]...")

    query_fn = (
        (lambda q: query_local_model(model, q))
        if local
        else (lambda q: query_hf_inference(model, q))
    )

    result, per_question = run_eval(query_fn, questions)

    table = Table(title=f"Results: {model}")
    table.add_column("Metric")
    table.add_column("Value")
    table.add_row("Total questions", str(result.total))
    table.add_row("Accuracy", f"{result.accuracy:.1%}")
    table.add_row("Confidently wrong", f"{result.confidently_wrong_rate:.1%}")
    table.add_row("Refusal rate", f"{result.refusal_rate:.1%}")
    console.print(table)

    if output:
        with open(output, "w", encoding="utf-8") as f:
            json.dump({
                "model": model,
                "accuracy": result.accuracy,
                "confidently_wrong_rate": result.confidently_wrong_rate,
                "refusal_rate": result.refusal_rate,
                "details": per_question,
            }, f, indent=2)
        console.print(f"Saved results to {output}")


if __name__ == "__main__":
    main()