"""TUI screens for different modes."""

from .mode1_input import Mode1InputScreen
from .mode1_comprehensive import Mode1ComprehensiveScreen
from .mode2_input import Mode2InputScreen
from .mode2_matrix import Mode2MatrixScreen
from .mode3_setup import Mode3SetupScreen
from .mode3_quiz import Mode3QuizScreen
from .mode3_results import Mode3ResultsScreen

__all__ = [
    "Mode1InputScreen",
    "Mode1ComprehensiveScreen",
    "Mode2InputScreen",
    "Mode2MatrixScreen",
    "Mode3SetupScreen",
    "Mode3QuizScreen",
    "Mode3ResultsScreen",
]
