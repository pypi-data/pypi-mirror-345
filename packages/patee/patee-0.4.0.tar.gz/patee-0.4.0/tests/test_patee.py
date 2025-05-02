from pathlib import Path

from patee.patee import Patee
from tests.utils.fakes.step_fakes import FakeStepsBuilder
from tests.utils.mothers.sources import (
    get_existing_monolingual_single_file_pair,
    PIPELINES_DIR
)

FAKES_CONFIG = PIPELINES_DIR / "just_for_tests.yml"

OUT_DIR = Path(__file__).parent / "out"


class TestPatee:
    def test_load_with_fake_builder_patee(self):
        builder = FakeStepsBuilder()
        patee = Patee.load_from(FAKES_CONFIG, steps_builder=builder)

        assert patee.step_names == ["00_extract", "01_process"]


    def test_patee_can_remove_steps(self):
        builder = FakeStepsBuilder()
        patee = Patee.load_from(FAKES_CONFIG, steps_builder=builder)
        patee.remove_step("00_extract")

        assert patee.step_names == ["01_process"]

    def test_patee_can_process_without_out_dir(self):
        builder = FakeStepsBuilder()
        patee = Patee.load_from(FAKES_CONFIG, steps_builder=builder)

        source = get_existing_monolingual_single_file_pair()

        result = patee.run(source)

        assert result.status == "succeeded"
        assert result.executed_steps == frozenset()
        assert result.skipped_steps == frozenset()
        assert result.non_succeeded_reason is None

    def test_patee_can_process_with_out_dir(self):
        builder = FakeStepsBuilder()
        patee = Patee.load_from(FAKES_CONFIG, steps_builder=builder)

        source = get_existing_monolingual_single_file_pair()

        OUT_DIR.mkdir(parents=True, exist_ok=True)

        result = patee.run(source, OUT_DIR)

        assert result.status == "succeeded"
        assert result.executed_steps == frozenset()
        assert result.skipped_steps == frozenset()
        assert result.non_succeeded_reason is None