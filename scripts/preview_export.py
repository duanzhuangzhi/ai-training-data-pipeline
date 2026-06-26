from __future__ import annotations

import json
from pathlib import Path


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    export_path = project_root / "data" / "exports" / "instruction_dataset.jsonl"
    if not export_path.exists():
        raise SystemExit("Export file not found. Run scripts/run_pipeline.py first.")

    print("Instruction dataset preview:\n")
    with export_path.open("r", encoding="utf-8") as file:
        for index, line in enumerate(file, start=1):
            record = json.loads(line)
            print(f"[{index}] {record['category']} | score={record['quality_score']}")
            print(f"Q: {record['instruction']}")
            print(f"A: {record['output'][:90]}")
            print()
            if index >= 5:
                break


if __name__ == "__main__":
    main()

