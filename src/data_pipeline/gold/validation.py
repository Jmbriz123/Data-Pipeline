from datetime import datetime, timezone

import pandas as pd


def apply_business_logic(df: pd.DataFrame) -> pd.DataFrame:
    today = pd.Timestamp(datetime.now(timezone.utc).date())

    has_reward = df["num_reward_days"].notna() & (df["num_reward_days"] > 0)
    is_berhasil = df["referral_status"] == "Berhasil"
    is_pending_or_failed = df["referral_status"].isin(["Menunggu", "Tidak Berhasil"])
    has_txn = df["effective_transaction_id"].notna()
    txn_paid = df["transaction_status"].fillna("").str.lower() == "paid"
    txn_new = df["transaction_type"].fillna("").str.lower() == "new"
    txn_after_ref = df["transaction_at"] > df["referral_at_local"]
    txn_same_month = (
        df["transaction_at"].dt.to_period("M") ==
        df["referral_at_local"].dt.to_period("M")
    )
    membership_valid = df["membership_expired_date"] >= today
    not_deleted = df["is_deleted"].fillna(False) == False
    reward_granted = df["is_reward_granted"].fillna(False) == True

    valid_c1 = (
        has_reward &
        is_berhasil &
        has_txn &
        txn_paid &
        txn_new &
        txn_after_ref &
        txn_same_month &
        membership_valid &
        not_deleted &
        reward_granted
    )

    valid_c2 = is_pending_or_failed & ~has_reward

    invalid_c1 = has_reward & ~is_berhasil
    invalid_c2 = has_reward & ~has_txn
    invalid_c3 = ~has_reward & has_txn & txn_paid & txn_after_ref
    invalid_c4 = is_berhasil & ~has_reward
    invalid_c5 = has_txn & ~txn_after_ref

    is_invalid = invalid_c1 | invalid_c2 | invalid_c3 | invalid_c4 | invalid_c5
    is_valid = (valid_c1 | valid_c2) & ~is_invalid

    result = df.copy()
    result["is_business_logic_valid"] = is_valid
    return result
