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

\`\`\`bash
pip install f1-temporal-bench
\`\`\`

## Usage

\`\`\`bash
f1-temporal-bench validate
f1-temporal-bench run --model meta-llama/Llama-3.2-1B-Instruct
\`\`\`

## Metrics

- **Accuracy** — exact/alias match against ground truth
- **Confidently wrong rate** — model gives a specific, wrong answer
  instead of hedging
- **Refusal rate** — model declines to answer / says it doesn't know

## Contributing questions

Add new rows to \`data/questions.jsonl\` after each race weekend. Run
\`f1-temporal-bench validate\` before committing.

## Roadmap

- [ ] Automated dataset updates via GitHub Actions after each race
- [ ] Multi-model leaderboard published to GitHub Pages
- [ ] Dataset published on the Hugging Face Hub with versioned season snapshots