from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(project_root / "src"))

    from ai_data_pipeline.pipeline import run_pipeline

    parser = argparse.ArgumentParser(description="Run AI training data pipeline.")
    parser.add_argument("--min-export-score", type=int, default=60, help="Minimum quality score for exported samples.")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%H:%M:%S",
    )

    result = run_pipeline(project_root=project_root, min_export_score=args.min_export_score)

    print("\nPipeline finished.")
    print(f"Raw samples: {result['raw_count']}")
    print(f"Cleaned samples: {result['cleaned_count']}")
    print(f"Deduped samples: {result['deduped_count']}")
    print(f"Exported samples: {result['exported_count']}")
    print(f"Report: {result['report_path']}")
    print(f"Export: {result['export_path']}")


if __name__ == "__main__":
    main()

