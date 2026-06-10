import pandas as pd

from data_pipeline.cleaning import clean_lead_logs
from data_pipeline.transforms import assign_source_category
from data_pipeline.validation import apply_business_logic


def test_assign_source_category_for_lead_source():
    referrals = pd.DataFrame([
        {
            "referral_id": "r1",
            "referral_source": "Lead",
            "referee_id": "lead-123",
        }
    ])
    leads = pd.DataFrame([
        {"lead_id": "lead-123", "source_category": "Online"}
    ])

    result = assign_source_category(referrals, leads)

    assert result.loc[0, "referral_source_category"] == "Online"


def test_business_logic_identifies_invalid_referral_without_transaction():
    df = pd.DataFrame([
        {
            "referral_id": "r1",
            "referral_status": "Berhasil",
            "num_reward_days": 10,
            "effective_transaction_id": pd.NA,
            "transaction_status": pd.NA,
            "transaction_type": pd.NA,
            "transaction_at": pd.NaT,
            "referral_at_local": pd.to_datetime("2024-05-01 12:00:00"),
            "membership_expired_date": pd.to_datetime("2024-12-31"),
            "is_deleted": False,
            "is_reward_granted": True,
        }
    ])

    result = apply_business_logic(df)

    assert result.loc[0, "is_business_logic_valid"] == False


def test_clean_lead_logs_normalizes_status_fields():
    raw = pd.DataFrame([
        {"id": "1", "lead_id": "lead-1", "source_category": "ONLINE", "current_status": "pending", "created_at": "2024-05-01T00:00:00Z", "preferred_location": "A", "timezone_location": "Asia/Jakarta"}
    ])

    cleaned = clean_lead_logs(raw)

    assert cleaned.loc[0, "source_category"] == "Online"
    assert cleaned.loc[0, "current_status"] == "Pending"
    assert pd.api.types.is_datetime64_any_dtype(cleaned["created_at"])
