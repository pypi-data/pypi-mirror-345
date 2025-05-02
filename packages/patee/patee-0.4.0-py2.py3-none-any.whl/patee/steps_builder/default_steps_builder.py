from patee.step_types import StepsBuilder, Step
from patee.core_types import PipelineContext
from patee.steps.text_extractor_step import TextReaderExtractor
from patee.steps.docling_extractor_step import DoclingExtractor
from patee.steps.csv_extractor_step import CsvExtractor
from patee.steps.noop_processor_step import NoopProcessorStep
from patee.steps.human_in_the_loop_processor_step import HumanInTheLoopProcessorStep
from patee.steps.regex_filter_processor_step import RegexFilterStep
from patee.steps.regex_replace_processor_step import RegexReplaceStep
from patee.steps.text_writer_processor_step import TextWriterProcessorStep


class DefaultStepsBuilder(StepsBuilder):
    def __init__(self):
        super().__init__()
        self._supported_steps: set[str] = {
            # Extractors
            TextReaderExtractor.step_type(),
            DoclingExtractor.step_type(),
            CsvExtractor.step_type(),
            # Processors
            NoopProcessorStep.step_type(),
            HumanInTheLoopProcessorStep.step_type(),
            RegexFilterStep.step_type(),
            RegexReplaceStep.step_type(),
            # Persisters
            TextWriterProcessorStep.step_type(),
        }

    def get_supported_step_types(self) -> set[str]:
        return self._supported_steps

    def build(self, step_type: str, step_name: str, pipeline_contex: PipelineContext, **kwargs) -> Step:
        # Extractors
        if step_type == TextReaderExtractor.step_type():
            return TextReaderExtractor(step_name, pipeline_contex, **kwargs)
        elif step_type == DoclingExtractor.step_type():
            return DoclingExtractor(step_name, pipeline_contex, **kwargs)
        elif step_type == CsvExtractor.step_type():
            return CsvExtractor(step_name, pipeline_contex, **kwargs)
        # Processors
        elif step_type == NoopProcessorStep.step_type():
            return NoopProcessorStep(step_name, pipeline_contex, **kwargs)
        elif step_type == HumanInTheLoopProcessorStep.step_type():
            return HumanInTheLoopProcessorStep(step_name, pipeline_contex, **kwargs)
        elif step_type == RegexFilterStep.step_type():
            return RegexFilterStep(step_name, pipeline_contex, **kwargs)
        elif step_type == RegexReplaceStep.step_type():
            return RegexReplaceStep(step_name, pipeline_contex, **kwargs)
        # Persisters
        elif step_type == TextWriterProcessorStep.step_type():
            return TextWriterProcessorStep(step_name, pipeline_contex, **kwargs)
        else:
            raise ValueError(f"Unsupported step: {step_type}")
