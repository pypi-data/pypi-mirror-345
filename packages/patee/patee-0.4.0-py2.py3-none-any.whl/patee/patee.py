import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Union, Iterable, cast, FrozenSet

import yaml

from .core_types import PipelineContext, RunContext
from .input_types import MonolingualSingleFilePair, MultilingualSingleFile
from .step_types import (
    ParallelExtractStep,
    ParallelProcessStep,
    StepMetadata,
    DocumentPairContext,
)
from .steps_builder.default_steps_builder import StepsBuilder
from .steps_executor import NonPersistentStepsExecutor, PersistentStepsExecutor
from .steps_builder.default_steps_builder import DefaultStepsBuilder

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RunResult:
    status: str
    executed_steps: FrozenSet[str]
    skipped_steps: FrozenSet[str]
    non_succeeded_reason: str = None


class Patee:
    """Main pipeline class to coordinate the processing steps."""

    def __init__(self, context: PipelineContext, steps_builder: StepsBuilder):
        self._context = context
        self._steps_builder = steps_builder
        self._steps = []

    @property
    def step_names(self) -> Iterable[str]:
        """Return the name of the steps."""
        return [step.name for step, _ in self._steps]

    @classmethod
    def load_from(cls, config_path: Path, steps_builder: StepsBuilder = None) -> "Patee":
        # Validate the config file exists
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file {config_path} does not exist.")

        try:
            logger.debug("reading configuration file from %s ...", config_path)
            config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
             Exception("The config has invalid YAML syntax.", exc)

        pipeline_context = PipelineContext(
            config_path=config_path,
            execution_path=Path.cwd(),
        )

        if not steps_builder:
            logger.debug("no steps builder provided. Using default steps builder.")
            steps_builder = DefaultStepsBuilder()
        else:
            logger.debug("using provided steps builder: %s", steps_builder.__class__.__name__)
            steps_builder = steps_builder

        instance = cls(pipeline_context, steps_builder)

        step_idx = 0
        unique_step_names = set()
        for step in config["steps"]:
            step_type = step.get("type")
            if not step_type:
                raise ValueError("Step type is required in the configuration file.")

            logger.debug("loading step %s at position %s...", step_type, step_idx)

            step_name = step.get("name")
            if not step_name:
                step_name = step_type
            step_idx_name = f"{step_idx:02d}_{step_name.lower()}"

            if step_idx_name in unique_step_names:
                raise ValueError(f"Step names must be unique. Duplicate name found: {step_idx_name}")

            step_config = step.get("config")
            if not step_config:
                step_config = {}

            metadata = StepMetadata(
                type=step_type,
                name=step_idx_name,
                idx=step_idx,
                config_hash=hash(json.dumps(step_config, sort_keys=True, ensure_ascii=True)),
            )
            step_instance = instance._steps_builder.build(step_type, step_idx_name, pipeline_context, **step_config)

            instance._steps.append((step_instance, metadata))
            unique_step_names.add(step_idx_name)

            logger.debug("step %s with name %s loaded successfully.", step_type, step_idx_name)

            step_idx += 1

        logger.info("pipeline created successfully. Found %s step(s).", len(unique_step_names))

        return instance

    def remove_step(self, step_name: str) -> None:
        """Remove a step from the pipeline by name."""
        self._steps = [(step, metadata) for step, metadata in self._steps if step.name != step_name]

    def run(self, source: Union[MonolingualSingleFilePair, MultilingualSingleFile],
            out_dir: Union[Path, None] = None) -> RunResult:
        """Process source through the complete pipeline."""

        # Validate state of the pipeline is correct to start processing the source
        self._validate_steps_for_process()

        source_hash = str(hash(source))

        run_context = RunContext(
            source_hash=source_hash,
            output_dir=out_dir,
        )

        logger.info("start processing source with hash %s ...", source_hash)

        if out_dir is None:
            logger.debug("no output directory provided. creating a NonPersistentStepsExecutor steps executor.")
            executor = NonPersistentStepsExecutor(self._context, run_context)
        else:
            # Validate the directory exists
            if not out_dir.exists():
                raise FileNotFoundError(f"Output directory {out_dir} does not exist.")

            logger.debug(" output directory provided: %s. Creating a PersistentStepsExecutor steps executor.", out_dir)
            executor = PersistentStepsExecutor(self._context, run_context)


        extract_step, extract_metadata = self._steps[0]
        extract_result = executor.execute_step(cast(ParallelExtractStep ,extract_step), extract_metadata, source)

        step_result = extract_result
        for step, metadata in self._steps[1:]:
            step_result = executor.execute_step(cast(ParallelProcessStep ,step), metadata, step_result.context)

            if step_result.should_stop_pipeline:
                logger.warning("pipeline stopped at step %s with name %s.", metadata.type, metadata.name)
                break

        return RunResult(
            status="stopped" if step_result.should_stop_pipeline else "succeeded",
            non_succeeded_reason="Pipeline stopped by human in the loop step" if step_result.should_stop_pipeline else None,
            executed_steps=frozenset(),
            skipped_steps=frozenset(),
        )

    def _validate_steps_for_process(self):
        """Validate the steps in the pipeline."""
        if not self._steps:
            raise ValueError("No processing steps defined in the pipeline.")

        # Get the first step and validate is an instance of ExtractStep class
        first_step, _ = self._steps[0]
        if not isinstance(first_step, ParallelExtractStep):
            raise ValueError(f"First step must be an instance of ExtractStep, got {type(first_step)} instead.")

        # Validate that all other steps are instances of ParallelTextStep
        for step, _ in self._steps[1:]:
            if not isinstance(step, ParallelProcessStep):
                raise ValueError(f"All steps must be instances of ParallelTextStep, got {type(step)} instead.")





