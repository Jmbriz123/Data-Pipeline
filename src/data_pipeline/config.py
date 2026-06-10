import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PipelineConfig:
    bronze_dir: Path
    silver_dir: Path
    gold_dir: Path
    profiling_dir: Path

    def ensure_directories(self) -> None:
        for directory in (
            self.bronze_dir,
            self.silver_dir,
            self.gold_dir,
            self.profiling_dir,
        ):
            directory.mkdir(parents=True, exist_ok=True)


def default_config() -> PipelineConfig:
    bronze_dir = Path(os.getenv("DATA_DIR", "data"))
    silver_dir = Path(os.getenv("SILVER_DIR", "data/silver"))
    gold_dir = Path(os.getenv("OUTPUT_DIR", "output"))
    profiling_dir = Path(os.getenv("PROFILING_DIR", "profiling"))
    config = PipelineConfig(
        bronze_dir=bronze_dir,
        silver_dir=silver_dir,
        gold_dir=gold_dir,
        profiling_dir=profiling_dir,
    )
    config.ensure_directories()
    return config
