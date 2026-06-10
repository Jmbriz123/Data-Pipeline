#!/usr/bin/env python3
import argparse
import logging
import os
from pathlib import Path

from data_pipeline.config import PipelineConfig
from data_pipeline.runner import run_profiling


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )


def build_config(args: argparse.Namespace) -> PipelineConfig:
    data_dir = Path(args.data_dir or os.getenv("DATA_DIR", "data"))
    profiling_dir = Path(args.profiling_dir or os.getenv("PROFILING_DIR", "profiling"))
    config = PipelineConfig(
        bronze_dir=data_dir,
        silver_dir=Path(os.getenv("SILVER_DIR", "data/silver")),
        gold_dir=Path(os.getenv("OUTPUT_DIR", "output")),
        profiling_dir=profiling_dir,
    )
    config.ensure_directories()
    return config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the Springer Capital data profiling process."
    )
    parser.add_argument("--data-dir", help="Root bronze data directory", default=None)
    parser.add_argument("--profiling-dir", help="Profiling output directory", default=None)
    return parser.parse_args()


def main() -> None:
    configure_logging()
    args = parse_args()
    config = build_config(args)
    run_profiling(config=config)


if __name__ == "__main__":
    main()
