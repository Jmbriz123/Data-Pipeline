import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

TABLE_FILES = {
    "lead_logs": "lead_log.csv",
    "paid_transactions": "paid_transactions.csv",
    "referral_rewards": "referral_rewards.csv",
    "user_logs": "user_logs.csv",
    "user_referral_logs": "user_referral_logs.csv",
    "user_referral_statuses": "user_referral_statuses.csv",
    "user_referrals": "user_referrals.csv",
}


def load_raw_tables(bronze_dir: Path) -> dict[str, pd.DataFrame]:
    dataframes: dict[str, pd.DataFrame] = {}
    for table_name, filename in TABLE_FILES.items():
        path = bronze_dir / filename
        logger.info("Loading bronze table %s from %s", table_name, path)
        dataframes[table_name] = pd.read_csv(path, dtype=str)
    return dataframes


def save_csv(df: pd.DataFrame, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    logger.info("Saved CSV %s (%d rows)", path, len(df))
    return path


def save_tables(tables: dict[str, pd.DataFrame], output_dir: Path) -> None:
    for name, table in tables.items():
        path = output_dir / f"{name}.csv"
        save_csv(table, path)
