from patee.step_types import (
    StepResult,
    DocumentPairContext,
    StepMetadata,
    TEXT_BLOCK_SEPARATOR
)
from patee.steps_executor import (
    NonPersistentStepsExecutor,
    PersistentStepsExecutor,
    IntelligentPersistenceStepsExecutor,
)
from tests.utils.fakes.step_fakes import FakeExtractor, FakeProcessor
from tests.utils.mothers.sources import get_existing_monolingual_single_file_pair, get_existing_document_pair_context, \
    get_default_text_blocks
from utils.mothers.contexts import get_pipeline_context, get_run_context


class TestNonPersistentStepsExecutor:
    def test_extract_step_execution(self):
        # Setup
        pipeline_context = get_pipeline_context()
        run_context = get_run_context(output_dir=None)
        executor = NonPersistentStepsExecutor(pipeline_context, run_context)
        extract_step = FakeExtractor("extract_test", pipeline_context)
        metadata = StepMetadata(
            name="extract_test",
            type="extract_fake",
            idx=0,
            config_hash=123456,
        )
        source = get_existing_monolingual_single_file_pair()

        # Execute
        result = executor.execute_step(extract_step, metadata, source)

        # Verify
        assert extract_step.was_called
        assert isinstance(result, StepResult)
        assert isinstance(result.context, DocumentPairContext)
        assert result.context.document_1.text_blocks == ["fake text 1"]
        assert result.context.document_2.text_blocks == ["fake text 2"]
        assert not result.should_stop_pipeline
        assert not result.skipped

    def test_process_step_execution(self):
        # Setup
        pipeline_context = get_pipeline_context()
        run_context = get_run_context(output_dir=None)
        executor = NonPersistentStepsExecutor(pipeline_context, run_context)
        process_step = FakeProcessor("process_test", pipeline_context)
        metadata = StepMetadata(
            name="extract_test",
            type="extract_fake",
            idx=1,
            config_hash=123456,
        )

        source = get_existing_document_pair_context()

        # Execute
        result = executor.execute_step(process_step, metadata, source)

        # Verify
        default_text_blocks = [text + " fake" for text in get_default_text_blocks()]
        assert process_step.was_called
        assert isinstance(result, StepResult)
        assert isinstance(result.context, DocumentPairContext)
        assert result.context.document_1.text_blocks == default_text_blocks
        assert result.context.document_2.text_blocks == default_text_blocks
        assert not result.should_stop_pipeline
        assert not result.skipped


class TestPersistentStepsExecutor:
    def test_extract_step_execution(self, tmp_path):
        # Setup
        pipeline_context = get_pipeline_context()
        run_context = get_run_context(output_dir=tmp_path)
        executor = PersistentStepsExecutor(pipeline_context, run_context)
        extract_step = FakeExtractor("extract_test", pipeline_context)
        metadata = StepMetadata(
            name="extract_test",
            type="extract_fake",
            idx=0,
            config_hash=123456,
        )
        source = get_existing_monolingual_single_file_pair()

        # Execute
        result = executor.execute_step(extract_step, metadata, source)

        # Verify
        assert extract_step.was_called
        assert isinstance(result, StepResult)
        assert isinstance(result.context, DocumentPairContext)

        # Check files were written
        step_dir = tmp_path / "extract_test"
        assert step_dir.exists()
        assert (step_dir / "GUIA-PDDD_ES.txt").exists()
        assert (step_dir / "GUIA-PDDD.txt").exists()

        # Check file content
        assert (step_dir / "GUIA-PDDD_ES.txt").read_text() == "fake text 1"
        assert (step_dir / "GUIA-PDDD.txt").read_text() == "fake text 2"

    def test_process_step_execution(self, tmp_path):
        # Setup
        pipeline_context = get_pipeline_context()
        run_context = get_run_context(output_dir=tmp_path)
        executor = PersistentStepsExecutor(pipeline_context, run_context)
        process_step = FakeProcessor("process_test", pipeline_context)
        metadata = StepMetadata(
            name="extract_test",
            type="extract_fake",
            idx=1,
            config_hash=123456,
        )

        source = get_existing_document_pair_context()

        # Execute
        result = executor.execute_step(process_step, metadata, source)

        # Verify
        assert process_step.was_called
        assert isinstance(result, StepResult)
        assert isinstance(result.context, DocumentPairContext)

        # Check files were written
        step_dir = tmp_path / "process_test"
        assert step_dir.exists()
        assert (step_dir / "GUIA-PDDD_ES.txt").exists()
        assert (step_dir / "GUIA-PDDD.txt").exists()

        # Check file content
        default_text_blocks = [text + " fake" for text in get_default_text_blocks()]
        assert (step_dir / "GUIA-PDDD_ES.txt").read_text().split(TEXT_BLOCK_SEPARATOR) == default_text_blocks
        assert (step_dir / "GUIA-PDDD.txt").read_text().split(TEXT_BLOCK_SEPARATOR) == default_text_blocks

    def test_stop_pipeline_no_files_written(self, tmp_path):
        # Setup
        pipeline_context = get_pipeline_context()
        run_context = get_run_context(output_dir=tmp_path)
        executor = PersistentStepsExecutor(pipeline_context, run_context)
        extract_step = FakeExtractor("extract_test", pipeline_context, should_stop=True)
        metadata = StepMetadata(
            name="extract_test",
            type="extract_fake",
            idx=0,
            config_hash=123456,
        )
        source = get_existing_monolingual_single_file_pair()

        # Execute
        result = executor.execute_step(extract_step, metadata, source)

        # Verify
        assert extract_step.was_called
        assert isinstance(result, StepResult)
        assert result.context is None
        assert result.should_stop_pipeline

        # Check directory was created but no files were written
        step_dir = tmp_path / "extract_test"
        assert step_dir.exists()
        assert not (step_dir / "GUIA-PDDD_ES.txt").exists()
        assert not (step_dir / "GUIA-PDDD.txt").exists()


class TestIntelligentPersistenceStepsExecutor:
    def test_new_source_execution(self, tmp_path):
        # Setup
        pipeline_context = get_pipeline_context()
        run_context = get_run_context(output_dir=tmp_path, source_hash="test_hash")
        executor = IntelligentPersistenceStepsExecutor(pipeline_context, run_context)
        extract_step = FakeExtractor("extract_test", pipeline_context)
        metadata = StepMetadata(
            name="extract_test",
            type="extract_fake",
            idx=0,
            config_hash=123456,
        )
        source = get_existing_monolingual_single_file_pair()

        # Verify initial state
        assert not executor.source_has_been_previously_executed

        # Execute
        result = executor.execute_step(extract_step, metadata, source)

        # Verify
        assert extract_step.was_called
        assert isinstance(result, StepResult)
        assert isinstance(result.context, DocumentPairContext)

        # Check files were written
        step_dir = tmp_path / "extract_test"
        assert step_dir.exists()
        assert (step_dir / "GUIA-PDDD_ES.txt").exists()
        assert (step_dir / "GUIA-PDDD.txt").exists()

    def test_reuse_previous_execution(self, tmp_path):
        # Setup - create previously executed step results
        source_hash = "123456"
        step_dir = tmp_path / "process_test"
        step_dir.mkdir(parents=True, exist_ok=True)

        metadata = StepMetadata(
            name="extract_test",
            type="extract_fake",
            idx=1,
            config_hash=123456,
        )

        # Create marker files
        main_marker = tmp_path / ".patee"
        main_marker.write_text(f"{source_hash}\n")
        step_marker = step_dir / ".patee"
        source_step_hash = f"{source_hash}--{hash(metadata)}"
        step_marker.write_text(f"{source_step_hash}\n")

        # Create result files
        (step_dir / "GUIA-PDDD_ES.txt").write_text("Previously processed text")
        (step_dir / "GUIA-PDDD.txt").write_text("Previously processed text")

        # Setup executor and test sources
        pipeline_context = get_pipeline_context()
        run_context = get_run_context(output_dir=tmp_path, source_hash=source_hash)
        executor = IntelligentPersistenceStepsExecutor(pipeline_context, run_context)
        process_step = FakeProcessor("process_test", pipeline_context)


        source = get_existing_document_pair_context()

        # Verify initial state
        assert executor.source_has_been_previously_executed

        # Execute
        result = executor.execute_step(process_step, metadata, source)

        # Verify
        # Should not call the process method since it's using cached results
        assert not process_step.was_called
        assert isinstance(result, StepResult)
        assert isinstance(result.context, DocumentPairContext)
        assert result.context.document_1.text_blocks == ["Previously processed text"]
        assert result.context.document_2.text_blocks == ["Previously processed text"]
