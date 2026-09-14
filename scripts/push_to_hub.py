"""Push data/questions.jsonl to the Hugging Face Hub as a dataset."""

import json
from datasets import Dataset

HUB_REPO = "spragada4/f1-temporal-bench"  # <-- change this

def main():
    rows = []
    with open("data/questions.jsonl", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))

    ds = Dataset.from_list(rows)
    ds.push_to_hub(HUB_REPO)
    print(f"Pushed {len(rows)} rows to {HUB_REPO}")

if __name__ == "__main__":
    main()
