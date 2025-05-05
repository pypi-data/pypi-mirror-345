import sys
sys.path.append(".")

import pytest
from src.braintumorprediction import prediction

def test_mean():
    assert prediction.mean([1, 2, 3, 4, 5]) == 3