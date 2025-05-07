"""
Tests for the core module.
"""

from mbxai.core import hello_world

def test_hello_world():
    """Test the hello_world function."""
    assert hello_world() == "Hello from MBX AI!" 