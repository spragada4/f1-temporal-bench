"""Fetch the latest completed F1 race and append new dataset rows.

Uses the Jolpica-F1 API — the free, open-source, drop-in successor to
the deprecated Ergast API. https://github.com/jolpica/jolpica-f1
"""

import json
from pathlib import Path

import requests

API_BASE = "https://api.jolpi.ca/ergast/f1"
DATASET_PATH = Path("data/questions.jsonl")


def fetch_json(url: str) -> dict:
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()


def load_existing_ids(path: Path) -> set[str]:
    ids = set()
    if not path.exists():
        return ids
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                ids.add(json.loads(line)["id"])
    return ids


def build_rows() -> list[dict]:
    result_data = fetch_json(f"{API_BASE}/current/last/results.json")
    races = result_data["MRData"]["RaceTable"]["Races"]
    if not races:
        return []

    race = races[0]
    season = int(race["season"])
    round_num = int(race["round"])
    race_name = race["raceName"]
    date = race["date"]
    winner = race["Results"][0]["Driver"]
    winner_name = f"{winner['givenName']} {winner['familyName']}"

    rows = [{
        "id": f"{season}-r{round_num:02d}-winner",
        "date": date,
        "question": f"Who won the {season} {race_name}?",
        "answer": winner_name,
        "aliases": [winner["familyName"]],
        "category": "race_winner",
        "season": season,
        "round": round_num,
    }]

    standings_data = fetch_json(f"{API_BASE}/{season}/{round_num}/driverStandings.json")
    lists = standings_data["MRData"]["StandingsTable"]["StandingsLists"]
    if lists:
        standings = lists[0]["DriverStandings"]
        leader = standings[0]["Driver"]
        rows.append({
            "id": f"{season}-wdc-leader-r{round_num:02d}",
            "date": date,
            "question": f"Who was leading the {season} F1 drivers' championship after round {round_num} ({race_name})?",
            "answer": f"{leader['givenName']} {leader['familyName']}",
            "aliases": [leader["familyName"]],
            "category": "wdc_standings",
            "season": season,
            "round": round_num,
        })
        if len(standings) > 1:
            second = standings[1]["Driver"]
            rows.append({
                "id": f"{season}-wdc-second-r{round_num:02d}",
                "date": date,
                "question": f"Who was second in the {season} F1 drivers' championship after round {round_num}?",
                "answer": f"{second['givenName']} {second['familyName']}",
                "aliases": [second["familyName"]],
                "category": "wdc_standings",
                "season": season,
                "round": round_num,
            })

    cons_data = fetch_json(f"{API_BASE}/{season}/{round_num}/constructorStandings.json")
    cons_lists = cons_data["MRData"]["StandingsTable"]["StandingsLists"]
    if cons_lists:
        cons_leader = cons_lists[0]["ConstructorStandings"][0]["Constructor"]
        rows.append({
            "id": f"{season}-constructors-leader-r{round_num:02d}",
            "date": date,
            "question": f"Which team was leading the {season} F1 constructors' championship after round {round_num}?",
            "answer": cons_leader["name"],
            "aliases": [],
            "category": "constructors_standings",
            "season": season,
            "round": round_num,
        })

    return rows


def main():
    existing_ids = load_existing_ids(DATASET_PATH)
    new_rows = [r for r in build_rows() if r["id"] not in existing_ids]

    if not new_rows:
        print("No new questions to add.")
        return

    DATASET_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Ensure the file ends with a newline before appending, so a new
    # row never gets merged onto the previous line.
    needs_leading_newline = False
    if DATASET_PATH.exists() and DATASET_PATH.stat().st_size > 0:
        with DATASET_PATH.open("rb") as f:
            f.seek(-1, 2)
            needs_leading_newline = f.read(1) != b"\n"

    with DATASET_PATH.open("a", encoding="utf-8") as f:
        if needs_leading_newline:
            f.write("\n")
        for row in new_rows:
            f.write(json.dumps(row) + "\n")

    print(f"Added {len(new_rows)} new question(s):")
    for row in new_rows:
        print(f"  - {row['id']}: {row['question']}")


if __name__ == "__main__":
    main()
