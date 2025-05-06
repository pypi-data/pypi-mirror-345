import sys
sys.path.append('..')

import pytest
from src.pygye import calculation

def test_calculation():
    assert calculation.calculate(5,10) == 15



