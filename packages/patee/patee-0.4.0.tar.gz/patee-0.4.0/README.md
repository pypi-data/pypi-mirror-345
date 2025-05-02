# Patee

![test](https://github.com/hbiarge/patee/actions/workflows/test.yml/badge.svg)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/patee)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/patee)


Patee (Parallel Text Extraction and Processing Pipeline) is 
a Python library designed for processing and extracting text from monolingual 
or multilingual documents in different languages. 

It provides a flexible pipeline architecture for working with multilingual 
content.

The library allows users to extract, align, and process text across 
language pairs in a structured manner.

Installation:

```bash
pip install patee
```

## How it Works

Patee operates through a configurable pipeline system:

1. **Configuration**: Pipelines are defined in YAML files (e.g., [pdf.yml](https://github.com/hbiarge/patee/blob/main/samples/pipelines/pdf.yml) that specify processing steps.

2. **Source Documents**: The library works with document sources such as:
   - `MultilingualSingleFile`: Represents a single document mixing multiple languages
   - `MonolingualSingleFilePair`: Pairs two documents in different languages for parallel processing

3. **Processing Flow**: 
   - The pipeline is initialized with a configuration file
   - Documents are loaded into the pipeline
   - Each configured step is executed sequentially
   - Processing parameters can be controlled (e.g., page ranges via `PageInfo`)
   - Results are collected and made available after pipeline execution

4. **Execution**: The pipeline is executed via the `run()` method, which returns a result object indicating whether processing completed successfully.

### Run modes

Patee supports two run modes:

1. **Non-persistent**: All processing is done in memory, and step results are not saved

```python
result = pipeline.run(source)
```

2. **Persistent run**: Every step result is saved to disk, allowing for later retrieval and analysis

```python
result = pipeline.run(source, Path("path/to/dir"))
```

## Available Pipeline Steps

There are two types of pipelines available in Patee:

- **Extract steps**: Should be the first step in the pipeline and retrieves the 
initial texts pair to start the processing
- **Process steps**: Process the extracted texts and can be used in any order
after the first __extract__ step

### Available Extract Steps

- `text_reader_extractor`: Extract text from sources in text format (e.g., TXT)
- `docling_extractor`: Extracts text from different document formats using the [docling](https://github.com/docling-project/docling) library.
Supported formats include `PDF`, `DOCX`, `HTML` and more. The full list can be found [here](https://docling-project.github.io/docling/usage/supported_formats).

### Available Process Steps

- `noop_step_processor`: Test step that does nothing
- `human_in_the_loop_processor`: A step that requires human input to process the text

#### human_in_the_loop_processor details

This step only works in **persistent** mode. In **non-persistent mode**, it is ignored.

It stops the pipeline execution to perform a human revision/edition of the text.

In the first execution of the step:
- The text of the previous step is persisted
- A marker file is created (`patee_rename_me_to_done_when_human_in_the_loop_is_done`)
- The pipeline execution is stopped and returns a `stopped` execution result

When the human revision is done, the user should rename the marker file to `patee_done` and run the pipeline again.

The pipeline will then continue from the last step.

## Example Usage

You can explore different examples in the [samples](https://github.com/hbiarge/patee/tree/main/samples) directory.