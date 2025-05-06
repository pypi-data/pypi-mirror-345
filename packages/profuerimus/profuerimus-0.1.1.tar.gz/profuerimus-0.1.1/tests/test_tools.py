# tests/test_tools.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from profuerimus.tools import topla
from profuerimus import tools


def test_topla():
    assert topla(2, 3) == 5
from profuerimus import tools

def test_multiply():
    assert tools.multiply(2, 3) == 6
    assert tools.multiply(-1, 5) == -5

if __name__ == "__main__":
    test_topla()
    test_multiply()
    print("Tüm testler başarıyla geçti.")
