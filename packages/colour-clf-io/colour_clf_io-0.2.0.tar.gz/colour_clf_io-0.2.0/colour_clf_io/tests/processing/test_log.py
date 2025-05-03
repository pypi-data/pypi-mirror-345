"""Define the unit tests for the :mod:`colour.io.clf` module."""

__author__ = "Colour Developers"
__copyright__ = "Copyright 2013 Colour Developers"
__license__ = "BSD-3-Clause - https://opensource.org/licenses/BSD-3-Clause"
__maintainer__ = "Colour Developers"
__email__ = "colour-developers@colour-science.org"
__status__ = "Production"

import numpy as np

from colour_clf_io.tests.processing.test_common import (
    assert_ocio_consistency,
    rgb_sample_iter,
)


def assert_snippet_consistency(snippet: str, decimals: int = 5) -> None:
    """
    Evaluate the snippet with multiple values anc check that they are the same as the
    `ociochecklut` tools output.
    """
    for rgb in rgb_sample_iter():
        value_rgb = np.array(rgb)
        assert_ocio_consistency(
            value_rgb,
            snippet,
            f"Failed to assert consistency for {rgb}",
            decimals=decimals,
        )


class TestLog:
    """
    Define test for applying Log nodes from a CLF file.
    """

    def test_ocio_consistency_log_10(self) -> None:
        """
        Test that the execution is consistent with the OCIO reference.
        """

        example = """
        <Log inBitDepth="16f" outBitDepth="16f" style="log10">
        </Log>
        """
        assert_snippet_consistency(example)

    def test_ocio_consistency_anti_log_10(self) -> None:
        """
        Test that the execution is consistent with the OCIO reference.
        """

        example = """
        <Log inBitDepth="16f" outBitDepth="16f" style="antiLog10">
        </Log>
        """
        assert_snippet_consistency(example, decimals=4)

    def test_ocio_consistency_log_2(self) -> None:
        """
        Test that the execution is consistent with the OCIO reference.
        """

        example = """
        <Log inBitDepth="16f" outBitDepth="16f" style="log2">
        </Log>
        """
        assert_snippet_consistency(example, decimals=4)

    def test_ocio_consistency_anti_log_2(self) -> None:
        """
        Test that the execution is consistent with the OCIO reference.
        """

        example = """
        <Log inBitDepth="16f" outBitDepth="16f" style="antiLog2">
        </Log>
        """
        assert_snippet_consistency(example)

    def test_ocio_consistency_lin_to_log(self) -> None:
        """
        Test that the execution is consistent with the OCIO reference.
        """

        example = """
        <Log inBitDepth="32f" outBitDepth="32f" style="linToLog">
            <LogParams base="10" logSideSlope="0.256663" logSideOffset="0.584555"
                linSideSlope="0.9892" linSideOffset="0.0108"
            />
        </Log>
        """
        assert_snippet_consistency(example)

    def test_ocio_consistency_log_to_lin(self) -> None:
        """
        Test that the execution is consistent with the OCIO reference.
        """

        example = """
        <Log inBitDepth="32f" outBitDepth="32f" style="logToLin">
            <LogParams base="10" logSideSlope="0.256663" logSideOffset="0.584555"
                linSideSlope="0.9892" linSideOffset="0.0108"
            />
        </Log>
        """
        assert_snippet_consistency(example)

    def test_ocio_consistency_camera_lin_to_log(self) -> None:
        """
        Test that the execution is consistent with the OCIO reference.
        """

        example = """
        <Log inBitDepth="32f" outBitDepth="32f" style="cameraLinToLog">
            <Description>Linear to DJI D-Log</Description>
            <LogParams base="10" logSideSlope="0.256663" logSideOffset="0.584555"
                linSideSlope="0.9892" linSideOffset="0.0108" linSideBreak="0.0078"
                linearSlope="6.025"/>
        </Log>
        """
        assert_snippet_consistency(example)

    def test_ocio_consistency_camera_log_to_lin(self) -> None:
        """
        Test that the execution is consistent with the OCIO reference.
        """

        example = """
        <Log inBitDepth="32f" outBitDepth="32f" style="cameraLinToLog">
            <Description>Linear to DJI D-Log</Description>
            <LogParams base="10" logSideSlope="0.256663" logSideOffset="0.584555"
                linSideSlope="0.9892" linSideOffset="0.0108" linSideBreak="0.0078"
                linearSlope="6.025"/>
        </Log>
        """
        assert_snippet_consistency(example)
