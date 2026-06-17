import numpy as np
import pandas as pd
from zoneinfo import ZoneInfo


def replace_null_strings(df: pd.DataFrame) -> pd.DataFrame:
    return df.replace({"null": np.nan, "NULL": np.nan, "": np.nan})


def parse_timestamps(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], utc=True, errors="coerce")
    return df


def to_local(ts: pd.Timestamp, tz_str: str) -> pd.Timestamp | object:
    if pd.isna(ts) or pd.isna(tz_str):
        return pd.NaT
    try:
        return ts.astimezone(ZoneInfo(tz_str)).replace(tzinfo=None)
    except Exception:
        return pd.NaT


def initcap(series: pd.Series) -> pd.Series:
    return series.where(series.isna(), series.str.title())


def clean_reward_value(series: pd.Series) -> pd.Series:
    return (
        series.str.extract(r"(\d+)")[0]
              .astype(float)
              .astype("Int64")
    )


def clean_lead_logs(df: pd.DataFrame) -> pd.DataFrame:
    df = replace_null_strings(df)
    df = parse_timestamps(df, ["created_at"])
    df["id"] = df["id"].astype("Int64")
    df["source_category"] = initcap(df["source_category"])
    df["current_status"] = initcap(df["current_status"])
    return df.drop_duplicates(subset=["id"])


def clean_paid_transactions(df: pd.DataFrame) -> pd.DataFrame:
    df = replace_null_strings(df)
    df = parse_timestamps(df, ["transaction_at"])
    df["transaction_status"] = initcap(df["transaction_status"])
    df["transaction_type"] = initcap(df["transaction_type"])
    df["transaction_at_local"] = df.apply(
        lambda row: to_local(row["transaction_at"], row["timezone_transaction"]),
        axis=1,
    )
    return df.drop_duplicates(subset=["transaction_id"])


def clean_referral_rewards(df: pd.DataFrame) -> pd.DataFrame:
    df = replace_null_strings(df)
    df = parse_timestamps(df, ["created_at"])
    df["id"] = df["id"].astype("Int64")
    df["reward_value"] = clean_reward_value(df["reward_value"])
    df["reward_type"] = pd.to_numeric(df["reward_type"], errors="coerce").astype("Int64")
    return df.drop_duplicates(subset=["id"])


def clean_user_logs(df: pd.DataFrame) -> pd.DataFrame:
    df = replace_null_strings(df)
    df["id"] = df["id"].astype("Int64")
    df["membership_expired_date"] = pd.to_datetime(df["membership_expired_date"], errors="coerce")
    df["is_deleted"] = df["is_deleted"].str.lower().map({"true": True, "false": False})
    return df.drop_duplicates(subset=["user_id"])


def clean_user_referral_logs(df: pd.DataFrame) -> pd.DataFrame:
    df = replace_null_strings(df)
    df = parse_timestamps(df, ["created_at"])
    df["id"] = df["id"].astype("Int64")
    df["is_reward_granted"] = df["is_reward_granted"].str.upper().map({"TRUE": True, "FALSE": False})
    return df.drop_duplicates(subset=["id"])


def clean_user_referral_statuses(df: pd.DataFrame) -> pd.DataFrame:
    df = replace_null_strings(df)
    df = parse_timestamps(df, ["created_at"])
    df["id"] = df["id"].astype("Int64")
    return df.drop_duplicates(subset=["id"])


def clean_user_referrals(df: pd.DataFrame) -> pd.DataFrame:
    df = replace_null_strings(df)
    df = parse_timestamps(df, ["referral_at", "updated_at"])
    df["user_referral_status_id"] = df["user_referral_status_id"].astype("Int64")
    df["referral_reward_id"] = pd.to_numeric(df["referral_reward_id"], errors="coerce").astype("Int64")
    df["referee_name"] = initcap(df["referee_name"])
    return df.drop_duplicates(subset=["referral_id"])


def clean_all_tables(raw_tables: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    return {
        "lead_logs": clean_lead_logs(raw_tables["lead_logs"]),
        "paid_transactions": clean_paid_transactions(raw_tables["paid_transactions"]),
        "referral_rewards": clean_referral_rewards(raw_tables["referral_rewards"]),
        "user_logs": clean_user_logs(raw_tables["user_logs"]),
        "user_referral_logs": clean_user_referral_logs(raw_tables["user_referral_logs"]),
        "user_referral_statuses": clean_user_referral_statuses(raw_tables["user_referral_statuses"]),
        "user_referrals": clean_user_referrals(raw_tables["user_referrals"]),
    }
