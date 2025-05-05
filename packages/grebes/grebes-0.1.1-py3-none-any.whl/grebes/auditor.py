import pandas as pd
import numpy as np
import json
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
import os

class GrebesAuditor:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.console = Console()

    def _fmt_val(self, v):
        if isinstance(v, np.generic): return v.item()
        if isinstance(v, (pd.Timestamp, datetime)): return v.strftime("%Y-%m-%d")
        return v

    def _sparkline(self, series: pd.Series, bins: int = 8) -> str:
        data = series.dropna().values
        if data.size == 0: return ""
        hist, _ = np.histogram(data, bins=bins)
        max_count = hist.max()
        blocks = "▁▂▃▄▅▆▇█"
        return "".join(blocks[int(h / max_count * (len(blocks) - 1))] for h in hist)

    def _show_unique(self, series: pd.Series) -> bool:
        return series.nunique(dropna=True) / len(series) <= 0.5

    def _show_sample(self, series: pd.Series) -> bool:
        return self._show_unique(series)

    def summarize(self) -> dict:
        df = self.df
        report = {
            "shape": list(df.shape),
            "memory_kb": round(df.memory_usage(deep=True).sum() / 1024, 2),
            "columns": {},
            "duplicates": int(df.duplicated().sum())
        }

        for col in df.columns:
            s = df[col]
            col_report = {
                "dtype": str(s.dtype),
                "missing_count": int(s.isnull().sum()),
                "missing_percent": round(s.isnull().mean() * 100, 1),
            }

            if self._show_unique(s):
                col_report["unique"] = int(s.nunique(dropna=True))
                col_report["sample_values"] = [self._fmt_val(v) for v in s.dropna().unique()[:3]]

            if pd.api.types.is_numeric_dtype(s):
                desc = s.dropna().describe()
                outliers = ((s < desc["25%"] - 1.5*(desc["75%"]-desc["25%"])) |
                            (s > desc["75%"] + 1.5*(desc["75%"]-desc["25%"]))).sum()
                col_report["stats"] = {
                    "mean": round(desc["mean"], 2),
                    "std": round(desc["std"], 2),
                    "min": round(desc["min"], 2),
                    "max": round(desc["max"], 2),
                    "outliers": int(outliers)
                }

            elif pd.api.types.is_datetime64_any_dtype(s):
                col_report["range"] = [
                    s.min().strftime('%Y-%m-%d'),
                    s.max().strftime('%Y-%m-%d')
                ]

            elif pd.api.types.is_object_dtype(s) or pd.api.types.is_categorical_dtype(s):
                if self._show_unique(s):
                    top = s.value_counts(dropna=True).head(3)
                    col_report["top_values"] = {
                        self._fmt_val(v): int(c) for v, c in top.items()
                    }

            if s.map(type).nunique() > 1:
                col_report["warning"] = "mixed types detected"

            report["columns"][col] = col_report

        return report

    def print_report(self):
        self.console.print(
            Panel(Text("🧠 GREBES DIAGNOSTIC REPORT", justify="center", style="bold white on dark_green"), expand=True)
        )
        summary = self.summarize()
        df_shape = summary["shape"]
        self.console.print(f"[bold]Rows:[/] {df_shape[0]:,}   [bold]Cols:[/] {df_shape[1]}   [bold]Mem:[/] {summary['memory_kb']} KB\n")

        for col, data in summary["columns"].items():
            tbl = Table.grid(padding=(0,1))
            tbl.add_column("Metric", style="bold")
            tbl.add_column("Value")

            tbl.add_row("Type", data["dtype"])
            tbl.add_row("Missing", f"{data['missing_count']} ({data['missing_percent']}%)")

            if "unique" in data:
                tbl.add_row("Unique", str(data["unique"]))
            if "sample_values" in data:
                tbl.add_row("Sample", ", ".join(map(str, data["sample_values"])))
            if "stats" in data:
                s = data["stats"]
                tbl.add_row("Stats", f"μ={s['mean']}, σ={s['std']}, min={s['min']}, max={s['max']}, out={s['outliers']}")
                tbl.add_row("Dist", self._sparkline(self.df[col]))
            if "range" in data:
                tbl.add_row("Range", " → ".join(data["range"]))
            if "top_values" in data:
                tops = ", ".join(f"{k}({v})" for k,v in data["top_values"].items())
                tbl.add_row("Top", tops)
            if "warning" in data:
                tbl.add_row("⚠️ Warning", data["warning"])

            self.console.print(Panel(tbl, title=f"[cyan]{col}[/]", border_style="cyan"))

        if summary["duplicates"]:
            self.console.print(Panel(f":warning: [bold red]{summary['duplicates']:,} duplicate rows[/]", border_style="red"))

    def save(self, path: str):
        report = self.summarize()
        ext = os.path.splitext(path)[1].lower()
        with open(path, "w", encoding="utf-8") as f:
            if ext == ".json":
                json.dump(report, f, indent=2)
            elif ext in {".md", ".markdown"}:
                f.write(f"# GREBES Report\n\nRows: {report['shape'][0]}  \nCols: {report['shape'][1]}  \nMemory: {report['memory_kb']} KB\n\n")
                for col, d in report["columns"].items():
                    f.write(f"## {col} ({d['dtype']})\n")
                    f.write(f"- Missing: {d['missing_count']} ({d['missing_percent']}%)\n")
                    for key in ["unique", "sample_values", "range", "warning"]:
                        if key in d:
                            f.write(f"- {key.replace('_', ' ').title()}: {d[key]}\n")
                    if "stats" in d:
                        stats = d["stats"]
                        f.write(f"- Stats: μ={stats['mean']}, σ={stats['std']}, min={stats['min']}, max={stats['max']}, outliers={stats['outliers']}\n")
                    if "top_values" in d:
                        tops = ", ".join(f"{k}({v})" for k,v in d["top_values"].items())
                        f.write(f"- Top: {tops}\n")
                    f.write("\n")
            else:
                raise ValueError("Only .json and .md supported for --output")
