import pytest
from unittest.mock import MagicMock

class MockF:
    def __init__(self):
        self.otype = MagicMock()
        self.book = MagicMock()
        self.chapter = MagicMock()
        self.verse = MagicMock()
        self.text = MagicMock()
        self.text.v.return_value = "Mock Verse Text"
    
class MockL:
    def __init__(self):
        self.d = MagicMock()
        self.d.return_value = [] # Default to empty list of children

class MockT:
    def __init__(self):
        self.sectionFromNode = MagicMock()
        self.text = MagicMock()
        self.text.return_value = "Mock Greek Text"

class MockApi:
    def __init__(self):
        self.F = MockF()
        self.L = MockL()
        self.T = MockT()

class MockApp:
    def __init__(self):
        self.api = MockApi()
        self.nodeFromSectionStr = MagicMock()

@pytest.fixture
def mock_app():
    return MockApp()

@pytest.fixture
def mock_printer():
    printer = MagicMock()
    printer.print_verse = MagicMock()
    printer.get_french_text.return_value = "Mock French Text"
    return printer
