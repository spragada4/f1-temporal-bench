# F1 Temporal Knowledge Benchmark

A benchmark for measuring how well language models track fast-changing,
verifiable facts — using Formula 1 standings, results, and records as
ground truth. F1 facts change every ~2 weeks during the season, making
this domain a natural, continuously-refreshed test of temporal knowledge
and hallucination in LLMs.

## Why F1?

Most knowledge benchmarks go stale the moment a model is trained. F1
gives us a domain where "true as of last week" and "true as of last year"
are meaningfully different — a clean way to measure whether a model
knows what it knows, or confidently guesses.

## Install

```bash
pip install f1-temporal-bench
```

## Setup

Evaluating models requires a Hugging Face access token with **Inference
Providers** permission enabled.

1. Create a token at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
   (the default "Read" preset includes this)
2. Export it in your shell:

```bash
export HF_TOKEN=hf_your_token_here
```

3. Make sure at least one Inference Provider is enabled on your account at
   [huggingface.co/settings/inference-providers](https://huggingface.co/settings/inference-providers).
   This project currently queries models through **Featherless AI**, which
   hosts the broadest range of open instruct models — enable it there.

## Usage

```bash
# Check the dataset is well-formed
f1-temporal-bench validate

# Evaluate a model via the HF Inference API
f1-temporal-bench run --model Qwen/Qwen2.5-7B-Instruct --output results.json

# Evaluate a model locally instead (requires the 'local-models' extra)
pip install "f1-temporal-bench[local-models]"
f1-temporal-bench run --model Qwen/Qwen2.5-7B-Instruct --local
```

### Picking a model

Not every model on the Hub is served by an Inference Provider. Before
running an eval, you can check what's live for a given model:

```bash
curl -s "https://huggingface.co/api/models/MODEL_ID?expand[]=inferenceProviderMapping" | python3 -m json.tool
```

Look for an entry with `"status": "live"` — that's the provider that will
serve the request.

## Metrics

- **Accuracy** — exact/alias match against ground truth
- **Confidently wrong rate** — model gives a specific, wrong answer
  instead of hedging
- **Refusal rate** — model declines to answer / says it doesn't know

## Dataset

The question set is also published as a dataset on the Hugging Face Hub:
[spragada4/f1-temporal-bench](https://huggingface.co/datasets/spragada4/f1-temporal-bench).
It's kept in sync with `data/questions.jsonl` in this repo — push updates
with `python scripts/push_to_hub.py` after adding new questions.

## Contributing questions

Add new rows to `data/questions.jsonl` after each race weekend. Each row
follows this schema:

```json
{"id": "unique-id", "date": "YYYY-MM-DD", "question": "...", "answer": "...", "aliases": ["..."], "category": "...", "season": 2026, "round": 1}
```

Run `f1-temporal-bench validate` before committing.

## Development

```bash
git clone https://github.com/spragada4/f1-temporal-bench.git
cd f1-temporal-bench
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e ".[dev]"
pytest
```

## Releases

Tagged pushes (`vX.Y.Z`) trigger an automated build, PyPI publish, and
GitHub Release via GitHub Actions. See `.github/workflows/release.yml`.

**Before tagging, always bump the version in `pyproject.toml` first.**
PyPI permanently rejects re-uploads of a version number that already
exists — if the tag doesn't match a version bump, the release workflow
fails at the publish step and never reaches the GitHub Release step
either (since publish runs first).

Checklist for cutting a release:

```bash
# 1. Bump the version
grep version pyproject.toml   # confirm current version
sed -i '' 's/version = "OLD"/version = "NEW"/' pyproject.toml

# 2. Commit and push the bump
git add pyproject.toml
git commit -m "Bump version to NEW"
git push origin main

# 3. Tag and push the tag
git tag vNEW
git push origin vNEW

# 4. Watch the Actions tab until both the PyPI publish
#    and GitHub Release steps go green
```

If a tag was pushed with the wrong version already baked in, delete and
recreate it after fixing the version:

```bash
git tag -d vNEW
git push origin :refs/tags/vNEW
git tag vNEW
git push origin vNEW
```

## Roadmap

- [ ] Automated dataset updates via GitHub Actions after each race
- [ ] Multi-model leaderboard published to GitHub Pages
- [ ] Dataset published on the Hugging Face Hub with versioned season snapshots

## License

MIT