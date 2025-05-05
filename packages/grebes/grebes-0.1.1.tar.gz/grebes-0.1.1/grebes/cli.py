import sys, os
import pandas as pd
from grebes.auditor import GrebesAuditor

def read_dataset(path: str) -> pd.DataFrame:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".csv":
        return pd.read_csv(path)
    if ext in {".xls", ".xlsx"}:
        return pd.read_excel(path)
    if ext in {".json", ".jsonl"}:
        return pd.read_json(path, lines=(ext == ".jsonl"))
    raise ValueError(f"Unsupported file type: {ext}")

def main():
    if len(sys.argv) < 2:
        print("Usage: grebes <file> [--output report.json|report.md]")
        sys.exit(1)

    path = sys.argv[1]
    output_path = None
    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_path = sys.argv[idx + 1]
        else:
            print("Missing value for --output")
            sys.exit(2)

    df = read_dataset(path)
    auditor = GrebesAuditor(df)
    auditor.print_report()

    if output_path:
        auditor.save(output_path)
        print(f"\n📝 Report saved to {output_path}")
