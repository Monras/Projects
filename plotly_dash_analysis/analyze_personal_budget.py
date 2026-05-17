from __future__ import annotations

from pathlib import Path

from src.personal_budget_analysis import (
    build_derived_budget_series,
    build_markdown_report,
    compute_budget_summary,
    load_personal_budget,
)


def main() -> None:
    project_root = Path(__file__).resolve().parent
    processed_dir = project_root / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    monthly = load_personal_budget()
    derived = build_derived_budget_series(monthly)
    summary = compute_budget_summary(derived)
    report = build_markdown_report(summary)

    metrics_out = processed_dir / "personal_budget_timeseries.csv"
    report_out = processed_dir / "personal_budget_analysis.md"

    derived.reset_index().to_csv(metrics_out, index=False)
    report_out.write_text(report, encoding="utf-8")

    print("Saved analysis outputs:")
    print(f"- {metrics_out}")
    print(f"- {report_out}")
    print("\nSummary:")
    for key, value in summary.items():
        print(f"- {key}: {value}")


if __name__ == "__main__":
    main()
