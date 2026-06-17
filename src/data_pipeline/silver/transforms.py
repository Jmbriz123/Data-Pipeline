import numpy as np
import pandas as pd
from zoneinfo import ZoneInfo

from .cleaning import initcap


def to_local(ts: pd.Timestamp, tz_str: str) -> pd.Timestamp | object:
    if pd.isna(ts) or pd.isna(tz_str):
        return pd.NaT
    try:
        return ts.astimezone(ZoneInfo(tz_str)).replace(tzinfo=None)
    except Exception:
        return pd.NaT


def adjust_referral_times(user_referrals: pd.DataFrame, user_logs: pd.DataFrame) -> pd.DataFrame:
    timezone_lookup = (
        user_logs[["user_id", "timezone_homeclub"]]
        .drop_duplicates(subset=["user_id"])
    )
    df = user_referrals.merge(
        timezone_lookup,
        left_on="referrer_id",
        right_on="user_id",
        how="left",
    ).drop(columns=["user_id"])

    df["timezone_homeclub"] = df["timezone_homeclub"].fillna("Asia/Jakarta")
    df["referral_at_local"] = df.apply(
        lambda row: to_local(row["referral_at"], row["timezone_homeclub"]),
        axis=1,
    )
    df["updated_at_local"] = df.apply(
        lambda row: to_local(row["updated_at"], row["timezone_homeclub"]),
        axis=1,
    )
    return df


def assign_source_category(user_referrals: pd.DataFrame, lead_logs: pd.DataFrame) -> pd.DataFrame:
    lead_source = lead_logs[["lead_id", "source_category"]].drop_duplicates(subset=["lead_id"])
    df = user_referrals.merge(
        lead_source.rename(
            columns={"lead_id": "referee_id", "source_category": "lead_source_category"}
        ),
        on="referee_id",
        how="left",
    )

    conditions = [
        df["referral_source"] == "User Sign Up",
        df["referral_source"] == "Draft Transaction",
        df["referral_source"] == "Lead",
    ]
    choices = ["Online", "Offline", df["lead_source_category"]]
    df["referral_source_category"] = np.select(conditions, choices, default=np.nan)
    return df.drop(columns=["lead_source_category"])


def build_master_report(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    ur = tables["user_referrals"]
    url = tables["user_referral_logs"]
    urs = tables["user_referral_statuses"]
    rr = tables["referral_rewards"]
    pt = tables["paid_transactions"]
    ul = tables["user_logs"]

    url_latest = (
        url.sort_values("created_at")
           .drop_duplicates(subset=["user_referral_id"], keep="last")
    )

    report = ur.merge(
        url_latest[
            ["user_referral_id", "source_transaction_id", "created_at", "is_reward_granted"]
        ].rename(
            columns={
                "user_referral_id": "referral_id",
                "created_at": "reward_granted_at",
            }
        ),
        on="referral_id",
        how="left",
    )

    report = report.merge(
        urs[["id", "description"]].rename(
            columns={"id": "user_referral_status_id", "description": "referral_status"}
        ),
        on="user_referral_status_id",
        how="left",
    )

    report = report.merge(
        rr[["id", "reward_value"]].rename(
            columns={"id": "referral_reward_id", "reward_value": "num_reward_days"}
        ),
        on="referral_reward_id",
        how="left",
    )

    report["effective_transaction_id"] = report["source_transaction_id"].combine_first(report["transaction_id"])

    report = report.merge(
        pt[["transaction_id", "transaction_status", "transaction_at_local", "transaction_location", "transaction_type"]].rename(
            columns={
                "transaction_id": "effective_transaction_id",
                "transaction_at_local": "transaction_at",
            }
        ),
        on="effective_transaction_id",
        how="left",
    )

    referrer_info = (
        ul[["user_id", "name", "phone_number", "homeclub", "membership_expired_date", "is_deleted"]]
        .rename(columns={
            "user_id": "referrer_id",
            "name": "referrer_name",
            "phone_number": "referrer_phone_number",
            "homeclub": "referrer_homeclub",
        })
        .drop_duplicates(subset=["referrer_id"])
    )
    report = report.merge(referrer_info, on="referrer_id", how="left")
    return report
