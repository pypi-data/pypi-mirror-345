import logging
from abc import abstractmethod, ABC
from pathlib import Path
from typing import Union

from .core_types import PipelineContext, RunContext
from .step_types import (
    ParallelExtractStep,
    ParallelProcessStep,
    StepContext,
    StepMetadata,
    DocumentContext,
    DocumentPairContext,
    StepResult,
    DocumentSource,
)
from .input_types import MonolingualSingleFile, MonolingualSingleFilePair, MultilingualSingleFile

logger = logging.getLogger(__name__)


class StepsExecutor(ABC):
    @abstractmethod
    def execute_step(self, step: Union[ParallelExtractStep, ParallelProcessStep], metadata: StepMetadata,
                     source: Union[MonolingualSingleFile, MonolingualSingleFilePair, MultilingualSingleFile, DocumentContext, DocumentPairContext]) -> StepResult:
        pass


class NonPersistentStepsExecutor(StepsExecutor):
    def __init__(self, pipeline_context: PipelineContext, run_context: RunContext):
        self._pipeline_context = pipeline_context
        self._run_context = run_context

    def execute_step(self, step: Union[ParallelExtractStep, ParallelProcessStep], metadata: StepMetadata,
                     source: Union[MonolingualSingleFile, MonolingualSingleFilePair, MultilingualSingleFile, DocumentContext, DocumentPairContext]) -> StepResult:
        logger.info("start executing %s step in non persistent mode...", step.name)

        context = StepContext(
            pipeline_context=self._pipeline_context,
            run_context=self._run_context,
            step_dir=None
        )

        if isinstance(step, ParallelExtractStep):
            if isinstance(source, MonolingualSingleFile) or isinstance(source, MonolingualSingleFilePair) or isinstance(source, MultilingualSingleFile):
                result = step.extract(context, source)
            else:
                raise ValueError(f"Invalid source type for {step.name} step: {type(source)}")
        elif isinstance(step, ParallelProcessStep):
            if isinstance(source, DocumentContext) or isinstance(source, DocumentPairContext):
                result = step.process(context, source)
            else:
                raise ValueError(f"Invalid source type for {step.name} step: {type(source)}")
        else:
            raise ValueError(f"step must be a subclass of either ParallelExtractStep or ParallelProcessStep: {type(step)}")

        logger.info("%s step executed in %s seconds.", step.name, 0)
        return result


class PersistentStepsExecutor(StepsExecutor):
    def __init__(self, pipeline_context: PipelineContext, run_context: RunContext):
        self._pipeline_context = pipeline_context
        self._run_context = run_context

    def execute_step(self, step: Union[ParallelExtractStep, ParallelProcessStep], metadata: StepMetadata,
                     source: Union[MonolingualSingleFilePair, MultilingualSingleFile, DocumentPairContext]) -> StepResult:
        step_dir = self._run_context.output_dir / step.name
        step_dir.mkdir(parents=True, exist_ok=True)

        logger.info("start executing %s step in persistent mode...", step.name)

        context = StepContext(
            pipeline_context=self._pipeline_context,
            run_context=self._run_context,
            step_dir=step_dir
        )

        if isinstance(step, ParallelExtractStep):
            if isinstance(source, MonolingualSingleFile) or isinstance(source, MonolingualSingleFilePair) or isinstance(
                    source, MultilingualSingleFile):
                result = step.extract(context, source)
            else:
                raise ValueError(f"Invalid source type for {step.name} step: {type(source)}")
        elif isinstance(step, ParallelProcessStep):
            if isinstance(source, DocumentContext) or isinstance(source, DocumentPairContext):
                result = step.process(context, source)
            else:
                raise ValueError(f"Invalid source type for {step.name} step: {type(source)}")
        else:
            raise ValueError(
                f"step must be a subclass of either ParallelExtractStep or ParallelProcessStep: {type(step)}")

        if not result.should_stop_pipeline:
            result.context.dump_to(step_dir)

        logger.info("%s step executed in %s seconds.", step.name, 0)

        return result


class IntelligentPersistenceStepsExecutor(StepsExecutor):
    def __init__(self,  pipeline_context: PipelineContext, run_context: RunContext):
        self._pipeline_context = pipeline_context
        self._run_context = run_context
        self.source_has_been_previously_executed = False

        main_marker_file = self._run_context.output_dir / ".patee"
        self._validate_directory(self._run_context.output_dir, main_marker_file, self._run_context.source_hash)

    def execute_step(self, step: Union[ParallelExtractStep, ParallelProcessStep], metadata: StepMetadata,
                     source: Union[MonolingualSingleFilePair, MultilingualSingleFile, DocumentPairContext]) -> StepResult:
        step_dir = self._run_context.output_dir / step.name
        step_dir.mkdir(parents=True, exist_ok=True)
        step_marker_file = step_dir / ".patee"
        source_step_hash = f"{self._run_context.source_hash}--{hash(metadata)}"

        has_been_executed, open_mode = self._has_been_executed(step_marker_file, source_step_hash)

        if has_been_executed:
            logger.info(
                "the step %s with hash %s have already been executed in %s. Skipping...",
                step.name, source_step_hash, step_dir)

            result = self._load_result_from_previous_execution(source, step_dir)

            return result
        else:
            logger.info("start executing %s step in persistent mode...", step.name)

            context = StepContext(
                pipeline_context=self._pipeline_context,
                run_context=self._run_context,
                step_dir=step_dir,
            )

            if isinstance(step, ParallelExtractStep):
                if isinstance(source, MonolingualSingleFile) or isinstance(source,
                                                                           MonolingualSingleFilePair) or isinstance(
                        source, MultilingualSingleFile):
                    result = step.extract(context, source)
                else:
                    raise ValueError(f"Invalid source type for {step.name} step: {type(source)}")
            elif isinstance(step, ParallelProcessStep):
                if isinstance(source, DocumentContext) or isinstance(source, DocumentPairContext):
                    result = step.process(context, source)
                else:
                    raise ValueError(f"Invalid source type for {step.name} step: {type(source)}")
            else:
                raise ValueError(
                    f"step must be a subclass of either ParallelExtractStep or ParallelProcessStep: {type(step)}")

            if not result.should_stop_pipeline:
                result.context.dump_to(step_dir)

            # Save the hash of the source step to the marker file
            with step_marker_file.open(open_mode, encoding="utf-8") as f:
                f.write(source_step_hash + "\n")

            logger.info("%s step executed in %s seconds", step.name, 0)

            return result

    @staticmethod
    def _has_been_executed(step_marker_file: Path, source_step_hash: str) -> (bool, str):
        if step_marker_file.exists():
            for existing_hash in step_marker_file.read_text(encoding="utf-8").splitlines():
                if existing_hash == source_step_hash:
                    return True, "a"
            return False, "a"
        else:
            return False, "w"

    @staticmethod
    def _get_document_sources(
            source: Union[MonolingualSingleFilePair, MultilingualSingleFile, DocumentPairContext],
    ) -> (DocumentSource, DocumentSource):
        if isinstance(source, MonolingualSingleFilePair):
            return (
                DocumentSource.from_monolingual_file(source.document_1),
                DocumentSource.from_monolingual_file(source.document_2),
            )
        elif isinstance(source, MultilingualSingleFile):
            return (
                DocumentSource.from_multilingual_file(source, 0),
                DocumentSource.from_multilingual_file(source, 1),
            )
        elif isinstance(source, DocumentPairContext):
            return source.document_1.source, source.document_2.source
        else:
            raise ValueError("Unknown source type")

    def _validate_directory(self, base_dir: Path, main_marker_file: Path, source_hash: str):
        has_been_executed, open_mode = self._has_been_executed(main_marker_file, source_hash)
        if has_been_executed:
            logger.info("the source with hash %s has been executed before in %s", source_hash, base_dir)
            self.source_has_been_previously_executed = True
        else:
            logger.info("the source with hash %s has not been executed before in %s", source_hash, base_dir)
            self.source_has_been_previously_executed = False

        with main_marker_file.open(open_mode, encoding="utf-8") as f:
            f.write(source_hash + "\n")


    def _load_result_from_previous_execution(self, source, step_dir: Path) -> StepResult:
        document_1_source, document_2_source = self._get_document_sources(source)

        logger.debug("reading document 1 ...")
        document_1_context = document_1_source.create_context_executed_step(step_dir)
        logger.debug("reading document 2 ...")
        document_2_context = document_2_source.create_context_executed_step(step_dir)

        result = StepResult(
            context=DocumentPairContext(
                document_1=document_1_context,
                document_2=document_2_context,
            ),
            skipped=True,
        )
        return result
