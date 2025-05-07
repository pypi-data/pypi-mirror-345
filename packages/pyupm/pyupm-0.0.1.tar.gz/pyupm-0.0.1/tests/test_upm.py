import pytest
from pyupm import summation

def test_summation():
    assert summation(3,5) == 8

if __name__ == "__main__":
    pytest.main()