import logging
from pathlib import Path

from .config import default_config, PipelineConfig
from .bronze.io import load_raw_tables, save_csv, save_tables
from .bronze.profiling import profile_tables
from .silver.cleaning import clean_all_tables
from .silver.transforms import adjust_referral_times, assign_source_category, build_master_report
from .gold.report import finalise_report
from .gold.validation import apply_business_logic

logger = logging.getLogger(__name__)


def run_pipeline(
    config: PipelineConfig | None = None,
    save_silver: bool = True,
    profile: bool = True,
) -> Path:
    if config is None:
        config = default_config()

    logger.info("Starting data pipeline")
    raw_tables = load_raw_tables(config.bronze_dir)

    if profile:
        profile_tables(raw_tables, config.profiling_dir, stage="bronze")

    silver_tables = clean_all_tables(raw_tables)
    if save_silver:
        save_tables(silver_tables, config.silver_dir)

    if profile:
        profile_tables(silver_tables, config.profiling_dir, stage="silver")

    silver_tables["user_referrals"] = adjust_referral_times(
        silver_tables["user_referrals"], silver_tables["user_logs"]
    )
    silver_tables["user_referrals"] = assign_source_category(
        silver_tables["user_referrals"], silver_tables["lead_logs"]
    )

    report = build_master_report(silver_tables)
    report = apply_business_logic(report)
    report = finalise_report(report)

    output_path = config.gold_dir / "referral_report.csv"
    save_csv(report, output_path)
    logger.info("Pipeline finished, saved gold report to %s", output_path)
    return output_path


def run_profiling(config: PipelineConfig | None = None) -> None:
    if config is None:
        config = default_config()

    logger.info("Starting profiling run")
    raw_tables = load_raw_tables(config.bronze_dir)
    profile_tables(raw_tables, config.profiling_dir, stage="bronze")
    logger.info("Profiling run completed")
