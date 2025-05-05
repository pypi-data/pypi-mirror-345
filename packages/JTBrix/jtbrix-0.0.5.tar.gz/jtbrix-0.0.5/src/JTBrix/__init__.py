"""Top-level package for JTBrix."""

__author__ = """Amid Nayerhoda"""
__email__ = 'Nayerhoda@infn.it'
__version__ = '0.0.4'


# Import core functionality to the top level
from JTBrix.experiment import run_session  # Example: if you have a main entry point
from JTBrix.questionnaire import screens   # Example: expose a core class
from JTBrix.utils import port  # Example: utility functions
from JTBrix.ui import main  # Example: if you have a UI component
from JTBrix.screen_config import flow_config  # Example: if you have a configuration module
from JTBrix.experiment.run_experiment import run_test

__all__ = [
    "run_session",
    "screens",
    "port",
    "main",
    "flow_config",
    "run_test",
]