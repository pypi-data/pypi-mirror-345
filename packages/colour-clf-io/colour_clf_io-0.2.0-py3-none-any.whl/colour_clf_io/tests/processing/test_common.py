"""
Defines helper functionality for CLF tests.
"""

import os
import tempfile
from collections.abc import Generator
from typing import Any

import numpy as np
from colour.hints import NDArrayFloat
from colour.io.luts import AbstractLUTSequenceOperator

import colour_clf_io as clf
from colour_clf_io.processing import CLFProcessList

__all__ = [
    "assert_ocio_consistency",
    "assert_ocio_consistency_for_file",
    "snippet_to_process_list",
]

EXAMPLE_WRAPPER = """<?xml version="1.0" ?>
<ProcessList id="Example Wrapper" compCLFversion="3.0">
{0}
</ProcessList>
"""

RESOURCES_ROOT: str = os.path.join(os.path.dirname(__file__), "resources")


def wrap_snippet(snippet: str) -> str:
    """
    Takes a string that should contain the text representation of a CLF node, and
    returns valid CLF document. Essentially the given string is pasted into the
    `ProcessList` if a CLF document.

    This is useful to quickly convert example snippets of Process Nodes into valid CLF
    documents for parsing.
    """  # noqa: D401
    return EXAMPLE_WRAPPER.format(snippet)


def snippet_to_process_list(snippet: str) -> clf.ProcessList | None:
    """
    Takes a string that should contain a valid body for a XML Process List and
    returns the parsed `ProcessList`.
    """  # noqa: D401
    doc = wrap_snippet(snippet)
    return clf.read_clf(doc)


def snippet_as_tmp_file(snippet: str) -> str:
    doc = wrap_snippet(snippet)
    tmp_folder = tempfile.gettempdir()
    tmp_file_name = tempfile.mktemp(suffix=".clf")  # noqa: S306
    file_name = os.path.join(tmp_folder, tmp_file_name)
    with open(file_name, "w") as f:
        f.write(doc)
    return file_name


def ocio_output_for_file(
    path: str, rgb: tuple[float, float, float] | NDArrayFloat | None = None
) -> tuple[float, float, float]:
    """Apply a color transform file to a flattened, one-dimensional list of
    R,G,B values.
    """
    import PyOpenColorIO as ocio

    xform = ocio.FileTransform(src=path)  # pyright: ignore[reportAttributeAccessIssue]
    cpu = ocio.GetCurrentConfig().getProcessor(xform).getDefaultCPUProcessor()  # pyright: ignore[reportAttributeAccessIssue]
    result = cpu.applyRGB(rgb)
    # Note: depending on the input, `applyRGB` will either return the result data, or
    # modify the data in place. If the return value was `None` the data was modified
    # in place and we use that instead.
    if result is None:
        result = rgb
    assert result is not None
    return (result[0], result[1], result[2])


def ocio_output_for_snippet(
    snippet: str, rgb: tuple[float, float, float]
) -> NDArrayFloat:
    f = snippet_as_tmp_file(snippet)
    try:
        r, g, b = ocio_output_for_file(f, rgb)
        return np.array([r, g, b])
    finally:
        os.remove(f)


def result_as_array(result_text: str) -> NDArrayFloat:
    result_parts = result_text.strip().split()
    if len(result_parts) != 3:
        message = f"Invalid OCIO result: {result_text}"
        raise RuntimeError(message)
    result_values = list(map(float, result_parts))
    return np.array(result_values)


class SimpleRange(AbstractLUTSequenceOperator):
    def __init__(
        self, in_range: tuple[float, float], out_range: tuple[float, float]
    ) -> None:
        self.in_range = in_range
        self.out_range = out_range

    def apply(self, x: NDArrayFloat) -> NDArrayFloat:
        normalised = (x - self.in_range[0]) / (self.in_range[1] - self.in_range[0])
        return normalised * (self.out_range[1] - self.out_range[0]) + self.out_range[0]


class Normaliser(SimpleRange):
    def __init__(self, source_range: tuple[float, float]) -> None:
        super().__init__(source_range, (0.0, 1.0))


class Denormaliser(SimpleRange):
    def __init__(self, target_range: tuple[float, float]) -> None:
        super().__init__((0.0, 1.0), target_range)


def assert_ocio_consistency(
    value: NDArrayFloat, snippet: str, err_msg: str = "", decimals: int = 5
) -> None:
    """Assert that the colour library calculates the same output as the OCIO reference
    implementation for the given CLF snippet.
    """
    process_list = snippet_to_process_list(snippet)
    if process_list is None:
        err = "Invalid CLF snippet."
        raise AssertionError(err)
    lut_sequence = CLFProcessList(process_list)
    # apply_input_normalisation(process_list, lut_sequence)
    process_list_output = lut_sequence.apply(value, normalised_values=True)
    value_tuple = value[0], value[1], value[2]
    ocio_output = ocio_output_for_snippet(snippet, value_tuple)
    # Note: OCIO only accepts 16-bit floats so the precision agreement is limited.
    np.testing.assert_array_almost_equal(
        process_list_output, ocio_output, err_msg=err_msg, decimal=decimals
    )


def assert_ocio_consistency_for_file(value: NDArrayFloat, clf_path: str) -> None:
    """Assert that the colour library calculates the same output as the OCIO reference
    implementation for the given file.
    """

    process_list = clf.read_clf_from_file(clf_path)
    if process_list is None:
        err = "Invalid CLF snippet."
        raise AssertionError(err)
    lut_sequence = CLFProcessList(process_list)
    # apply_input_normalisation(process_list, lut_sequence)
    process_list_output = lut_sequence.apply(value, normalised_values=True)
    ocio_output = ocio_output_for_file(clf_path, value)
    np.testing.assert_array_almost_equal(process_list_output, ocio_output)


def rgb_sample_iter(
    step: float = 0.2,
) -> Generator[tuple[np.floating[Any], np.floating[Any], np.floating[Any]]]:
    for r in np.arange(0.0, 1.0, step):
        for g in np.arange(0.0, 1.0, step):
            for b in np.arange(0.0, 1.0, step):
                yield r, g, b
