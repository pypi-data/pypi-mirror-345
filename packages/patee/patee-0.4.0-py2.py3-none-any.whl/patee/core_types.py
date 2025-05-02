from dataclasses import dataclass
from pathlib import Path
from typing import Union


@dataclass
class PipelineContext:
    config_path: Path
    execution_path: Path


@dataclass
class RunContext:
    output_dir: Union[Path, None]
    source_hash: str


@dataclass(frozen=True)
class StepContext:
    pipeline_context: PipelineContext
    run_context: RunContext
    step_dir: Union[Path, None]
