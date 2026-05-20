# Import future annotations for type hints compatibility
from __future__ import annotations

# Import Path for file system operations
from pathlib import Path

# Import analysis functions from the personal budget analysis module
from src.personal_budget_analysis import (
    build_derived_budget_series,
    build_markdown_report,
    compute_budget_summary,
    load_personal_budget,
)


def main() -> None:
    """
    Main entry point for personal budget analysis.
    Loads budget data, performs analysis, and saves results to CSV and markdown reports.
    """
    # Get the project root directory and ensure the processed data directory exists
    project_root = Path(__file__).resolve().parent
    processed_dir = project_root / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    # Load raw monthly budget data from input source
    monthly = load_personal_budget()
    
    # Build derived metrics (calculated budget series from raw monthly data)
    derived = build_derived_budget_series(monthly)
    
    # Compute summary statistics from the derived metrics
    summary = compute_budget_summary(derived)
    
    # Generate a markdown formatted report from the summary
    report = build_markdown_report(summary)

    # Define output file paths for the timeseries data and analysis report
    metrics_out = processed_dir / "personal_budget_timeseries.csv"
    report_out = processed_dir / "personal_budget_analysis.md"

    # Save the derived metrics to a CSV file (resetting index for clean output)
    derived.reset_index().to_csv(metrics_out, index=False)
    
    # Save the markdown report to a text file
    report_out.write_text(report, encoding="utf-8")

    # Print confirmation messages with output file paths
    print("Saved analysis outputs:")
    print(f"- {metrics_out}")
    print(f"- {report_out}")
    
    # Print the summary metrics for quick review
    print("\nSummary:")
    for key, value in summary.items():
        print(f"- {key}: {value}")


# Execute main function when script is run directly (not imported)
if __name__ == "__main__":
    main()
