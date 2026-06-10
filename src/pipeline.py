#!/usr/bin/env python3
import argparse
import logging
import os
from pathlib import Path

from data_pipeline.config import PipelineConfig
from data_pipeline.runner import run_pipeline


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )


def build_config(args: argparse.Namespace) -> PipelineConfig:
    data_dir = Path(args.data_dir or os.getenv("DATA_DIR", "data"))
    silver_dir = Path(args.silver_dir or os.getenv("SILVER_DIR", "data/silver"))
    output_dir = Path(args.output_dir or os.getenv("OUTPUT_DIR", "output"))
    profiling_dir = Path(args.profiling_dir or os.getenv("PROFILING_DIR", "profiling"))
    config = PipelineConfig(
        bronze_dir=data_dir,
        silver_dir=silver_dir,
        gold_dir=output_dir,
        profiling_dir=profiling_dir,
    )
    config.ensure_directories()
    return config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the Springer Capital referral data pipeline."
    )
    parser.add_argument("--data-dir", help="Root bronze data directory", default=None)
    parser.add_argument("--silver-dir", help="Silver output directory", default=None)
    parser.add_argument("--output-dir", help="Gold report output directory", default=None)
    parser.add_argument("--profiling-dir", help="Profiling output directory", default=None)
    parser.add_argument("--no-profile", help="Skip profiling", action="store_true")
    parser.add_argument("--no-save-silver", help="Skip saving silver tables", action="store_true")
    return parser.parse_args()


def main() -> None:
    configure_logging()
    args = parse_args()
    config = build_config(args)
    run_pipeline(
        config=config,
        save_silver=not args.no_save_silver,
        profile=not args.no_profile,
    )


if __name__ == "__main__":
    main()
