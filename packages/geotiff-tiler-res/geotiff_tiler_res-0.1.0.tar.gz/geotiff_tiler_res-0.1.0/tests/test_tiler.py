import pytest
from geotiff_tiler.tiler import is_completely_black
import numpy as np

def test_is_completely_black():
    # Test completely black image
    image_data = np.zeros((3, 100, 100))
    assert is_completely_black(image_data, threshold=0, tolerance=0.001)

    # Test non-black image
    image_data = np.ones((3, 100, 100))
    assert not is_completely_black(image_data, threshold=0, tolerance=0.001)