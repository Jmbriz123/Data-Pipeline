import pandas as pd

from ..silver.cleaning import initcap

OUTPUT_COLUMNS = [
    "referral_details_id",
    "referral_id",
    "referral_source",
    "referral_source_category",
    "referral_at_local",
    "referrer_id",
    "referrer_name",
    "referrer_phone_number",
    "referrer_homeclub",
    "referee_id",
    "referee_name",
    "referee_phone",
    "referral_status",
    "num_reward_days",
    "effective_transaction_id",
    "transaction_status",
    "transaction_at",
    "transaction_location",
    "transaction_type",
    "updated_at_local",
    "reward_granted_at",
    "is_business_logic_valid",
]


def finalise_report(report: pd.DataFrame) -> pd.DataFrame:
    out = report.reset_index(drop=True).copy()
    out["referral_details_id"] = out.index + 101

    out = out[[col for col in OUTPUT_COLUMNS if col in out.columns]]
    out = out.rename(columns={
        "referral_at_local": "referral_at",
        "updated_at_local": "updated_at",
        "effective_transaction_id": "transaction_id",
    })

    for col in ["referral_at", "transaction_at", "updated_at", "reward_granted_at"]:
        if col in out.columns:
            out[col] = pd.to_datetime(out[col], errors="coerce").dt.strftime("%Y-%m-%d %H:%M:%S")

    initcap_cols = [
        "referral_source",
        "referral_source_category",
        "referral_status",
        "transaction_status",
        "transaction_type",
    ]
    for col in initcap_cols:
        if col in out.columns:
            out[col] = initcap(out[col])

    return out
