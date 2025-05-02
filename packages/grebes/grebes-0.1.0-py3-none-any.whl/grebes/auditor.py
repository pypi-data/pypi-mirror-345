# grebes/auditor.py

import pandas as pd
import numpy as np
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

class GrebesAuditor:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.console = Console()

    def _fmt_val(self, v):
        if isinstance(v, np.generic):
            return v.item()
        if isinstance(v, (pd.Timestamp, datetime)):
            return v.strftime("%Y-%m-%d")
        return v

    def _sparkline(self, series: pd.Series, bins: int = 8) -> str:
        data = series.dropna().values
        if data.size == 0:
            return ""
        hist, _ = np.histogram(data, bins=bins)
        max_count = hist.max()
        blocks = "▁▂▃▄▅▆▇█"
        return "".join(blocks[int(h / max_count * (len(blocks) - 1))] for h in hist)

    def _show_unique(self, series: pd.Series) -> bool:
        return series.nunique(dropna=True) / len(series) <= 0.5

    def _show_sample(self, series: pd.Series) -> bool:
        return self._show_unique(series)

    def print_report(self):
        df = self.df
        console = self.console

        # Header
        console.print(
            Panel(
                Text("🧠 GREBES DIAGNOSTIC REPORT", justify="center", style="bold white on dark_green"),
                expand=True
            )
        )
        console.print(f"[bold]Rows:[/] {len(df):,}   [bold]Cols:[/] {df.shape[1]}   [bold]Mem:[/] {df.memory_usage(deep=True).sum()/1024:.2f} KB\n")

        for col in df.columns:
            s = df[col]
            dtype = s.dtype
            missing = s.isnull().sum()
            miss_pct = missing * 100 / len(df)

            unique = s.nunique(dropna=True)
            sample_vals = ", ".join(str(self._fmt_val(v)) for v in s.dropna().unique()[:3]) or "-"

            # Build per-column table
            tbl = Table.grid(padding=(0,1))
            tbl.add_column("Metric", style="bold")
            tbl.add_column("Value")

            tbl.add_row("Type", str(dtype))
            tbl.add_row("Missing", f"{missing} ({miss_pct:.1f}%)")

            if self._show_unique(s):
                tbl.add_row("Unique", str(unique))

            if self._show_sample(s):
                tbl.add_row("Sample", sample_vals)

            if pd.api.types.is_numeric_dtype(s):
                desc = s.dropna().describe()
                outliers = ((s < desc["25%"] - 1.5*(desc["75%"]-desc["25%"])) |
                            (s > desc["75%"] + 1.5*(desc["75%"]-desc["25%"]))).sum()
                stats = f"μ={desc['mean']:.1f},σ={desc['std']:.1f},min={desc['min']:.1f},max={desc['max']:.1f},out={outliers}"
                tbl.add_row("Stats", stats)
                tbl.add_row("Dist", self._sparkline(s))

            elif pd.api.types.is_datetime64_any_dtype(s):
                mn, mx = s.min(), s.max()
                tbl.add_row("Range", f"{mn.strftime('%Y-%m-%d')} → {mx.strftime('%Y-%m-%d')}")

            elif pd.api.types.is_object_dtype(s) or pd.api.types.is_categorical_dtype(s):
                if self._show_unique(s):
                    top = s.value_counts(dropna=True).head(3)
                    tops = ", ".join(f"{self._fmt_val(v)}({cnt})" for v, cnt in top.items())
                    tbl.add_row("Top", tops)

            if s.map(type).nunique() > 1:
                tbl.add_row("⚠️ Warning", "Mixed types")

            console.print(Panel(tbl, title=f"[cyan]{col}[/]", border_style="cyan"))

        dupes = df.duplicated().sum()
        if dupes:
            console.print(
                Panel(f":warning: [bold red]{dupes:,} duplicate rows[/]", border_style="red")
            )
