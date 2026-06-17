import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


def profile_dataframe(table_name: str, df: pd.DataFrame) -> pd.DataFrame:
    total_rows = len(df)
    rows = []

    for col in df.columns:
        series = df[col]
        null_mask = series.isna() | series.astype(str).str.lower().eq("null")
        null_count = int(null_mask.sum())
        null_pct = round(null_count / total_rows * 100, 2) if total_rows else 0

        non_null = series[~null_mask]
        distinct = int(non_null.nunique())

        try:
            numeric = pd.to_numeric(non_null, errors="raise")
            min_val = numeric.min() if len(numeric) else None
            max_val = numeric.max() if len(numeric) else None
        except (ValueError, TypeError):
            min_val = non_null.min() if len(non_null) else None
            max_val = non_null.max() if len(non_null) else None

        max_len = int(non_null.astype(str).str.len().max()) if len(non_null) else 0

        rows.append({
            "table_name": table_name,
            "column_name": col,
            "data_type": str(series.dtype),
            "total_rows": total_rows,
            "null_count": null_count,
            "null_pct": null_pct,
            "populated_pct": round(100 - null_pct, 2),
            "distinct_count": distinct,
            "min_value": min_val,
            "max_value": max_val,
            "max_actual_length": max_len,
        })

    return pd.DataFrame(rows)


def profile_tables(
    tables: dict[str, pd.DataFrame],
    profiling_dir: Path,
    stage: str = "bronze",
) -> None:
    profiling_dir.mkdir(parents=True, exist_ok=True)

    summaries = []
    for table_name, df in tables.items():
        logger.info("Profiling %s stage table %s", stage, table_name)
        summaries.append(profile_dataframe(table_name, df))

    combined = pd.concat(summaries, ignore_index=True)
    csv_path = profiling_dir / f"data_profiling_report_{stage}.csv"
    combined.to_csv(csv_path, index=False)

    xlsx_path = profiling_dir / f"data_profiling_report_{stage}.xlsx"
    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
        combined.to_excel(writer, sheet_name="All Tables", index=False)
        for table_name in tables:
            subset = combined[combined["table_name"] == table_name]
            sheet = table_name[:31]
            subset.to_excel(writer, sheet_name=sheet, index=False)

    logger.info("Saved profiling reports for %s stage", stage)
