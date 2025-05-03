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


class TestLUT3D:
    """
    Define test for applying 3D LUTSs from a CLF file.
    """

    EXAMPLE_SIMPLE = """
    <LUT3D
        id="lut-24"
        name="green look"
        interpolation="trilinear"
        inBitDepth="12i"
        outBitDepth="16f"
    >
        <Description>3D LUT</Description>
        <Array dim="2 2 2 3">
            0.0 0.0 0.0
            0.0 0.0 1.0
            0.0 1.0 0.0
            0.0 1.0 1.0
            1.0 0.0 0.0
            1.0 0.0 1.0
            1.0 1.0 0.0
            1.0 1.0 1.0
        </Array>
    </LUT3D>
    """

    def test_ocio_consistency_simple(self) -> None:
        """
        Test that the execution of a simple 1D LUT is consistent with `ociochecklut`.
        """
        value_rgb = np.array([1.0, 0.5, 0.0])
        assert_ocio_consistency(value_rgb, self.EXAMPLE_SIMPLE)

    def test_ocio_consistency_tetrahedral_interpolation(self) -> None:
        """
        Test that the execution of a 1D LUT with tetrahedral interpolation is
        consistent with `ociochecklut`.
        """
        example = """
            <LUT3D
                id="lut-24"
                name="green look"
                interpolation="tetrahedral"
                inBitDepth="32f"
                outBitDepth="32f"
            >
                <Description>3D LUT</Description>
                <Array dim="2 2 2 3">
                    0.0 0.0 0.0
                    0.0 0.0 1.0
                    0.0 1.0 0.0
                    0.0 1.0 1.0
                    1.0 0.0 0.0
                    1.0 0.0 1.0
                    1.0 1.0 0.0
                    1.0 1.0 1.0
                </Array>
            </LUT3D>
            """
        for rgb in rgb_sample_iter():
            value_rgb = np.array(rgb)
            assert_ocio_consistency(value_rgb, example)
