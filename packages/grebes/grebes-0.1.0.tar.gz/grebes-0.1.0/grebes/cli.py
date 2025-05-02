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
        print("Usage: grebes <file.(csv|xlsx|json|jsonl)>")
        sys.exit(1)

    path = sys.argv[1]
    df = read_dataset(path)
    GrebesAuditor(df).print_report()
