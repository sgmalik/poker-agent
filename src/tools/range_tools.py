"""LangChain tools for GTO ranges and range parsing (Mode 2)."""

from typing import Any

from langchain_core.tools import tool

from ..core.gto_charts import GTOCharts
from ..core.range_parser import RangeParser


@tool
def get_gto_range(position: str, action: str = "open") -> dict[str, Any]:
    """
    Get the GTO (Game Theory Optimal) preflop range for a position and action.

    Args:
        position: The table position. Valid positions are:
            - UTG (Under the Gun - first to act)
            - UTG1 (UTG+1)
            - MP (Middle Position)
            - LJ (Lojack)
            - HJ (Hijack)
            - CO (Cutoff)
            - BTN (Button)
            - SB (Small Blind)
            - BB (Big Blind)
        action: The action type. Common actions include:
            - "open" - opening raise (RFI - Raise First In)
            - "call_vs_BTN" - calling vs button open (for BB)
            - "3bet_vs_BTN" - 3-betting vs button open

    Returns:
        Dictionary containing:
        - hands: List of hands in the range (e.g., ["AA", "KK", "AKs", ...])
        - notation: Compact range notation string
        - total_combos: Total number of hand combinations
        - percentage: Percentage of all possible starting hands

    Example:
        get_gto_range("BTN", "open") -> {"hands": ["AA", "KK", ...], "percentage": 40.0, ...}
    """
    try:
        charts = GTOCharts()

        # Normalize position
        position = position.upper()

        # Get available positions and validate
        valid_positions = charts.get_positions()
        if position not in valid_positions:
            return {
                "success": False,
                "error": f"Invalid position '{position}'. Valid positions: {', '.join(valid_positions)}",
            }

        # Get available actions for this position
        available_actions = charts.get_actions(position)
        if action not in available_actions:
            return {
                "success": False,
                "error": f"Action '{action}' not available for {position}. Available: {', '.join(available_actions)}",
            }

        range_data = charts.get_range(position, action)
        if not range_data:
            return {
                "success": False,
                "error": f"No range data found for {position} {action}",
            }

        return {
            "success": True,
            "position": position,
            "action": action,
            "hands": range_data.get("hands", []),
            "notation": range_data.get("notation", ""),
            "total_combos": range_data.get("total_combos", 0),
            "percentage": range_data.get("percentage", 0.0),
        }
    except Exception as e:
        return {"success": False, "error": f"Error getting range: {str(e)}"}


@tool
def list_available_ranges() -> dict[str, Any]:
    """
    List all available GTO range positions and their actions.

    Returns:
        Dictionary containing:
        - positions: Dict mapping each position to its available actions

    Example:
        list_available_ranges() -> {"positions": {"UTG": ["open"], "BTN": ["open"], "BB": ["call_vs_BTN", "3bet_vs_BTN"], ...}}
    """
    try:
        charts = GTOCharts()
        positions = charts.get_positions()

        result = {}
        for pos in positions:
            result[pos] = charts.get_actions(pos)

        return {"success": True, "positions": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


@tool
def parse_range(range_notation: str) -> dict[str, Any]:
    """
    Parse a poker range notation string into a list of hands and statistics.

    Args:
        range_notation: A range notation string using standard poker notation:
            - Single hands: AA, AKs, AKo
            - Plus notation: QQ+ (QQ and better pairs), ATs+ (ATs through AKs)
            - Range notation: QQ-88 (QQ through 88), A5s-A2s (A5s through A2s)
            - Combinations: "QQ+, AKs, ATs+, 98s"

    Returns:
        Dictionary containing:
        - hands: List of individual hands in the range
        - combos: Breakdown by type (pairs, suited, offsuit)
        - total_combos: Total number of combinations
        - percentage: Percentage of all 1326 possible starting hands

    Example:
        parse_range("QQ+, AKs, ATs+") -> {"hands": ["AA", "KK", "QQ", "AKs", "ATs", ...], "percentage": 5.2, ...}
    """
    try:
        parser = RangeParser()
        result = parser.parse(range_notation)

        return {
            "success": True,
            "input_notation": range_notation,
            "hands": result["hands"],
            "combos": result["combos"],
            "total_combos": result["total_combos"],
            "percentage": result["percentage"],
        }
    except ValueError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": f"Error parsing range: {str(e)}"}


@tool
def check_hand_in_range(
    hand: str, position: str, action: str = "open"
) -> dict[str, Any]:
    """
    Check if a specific hand is in a GTO range for a position and action.

    Args:
        hand: The hand to check (e.g., "AKs" for suited ace-king, "QQ" for pocket queens, "KJo" for offsuit king-jack)
        position: The table position (UTG, MP, CO, BTN, SB, BB, etc.)
        action: The action type (e.g., "open", "call_vs_BTN")

    Returns:
        Dictionary containing:
        - in_range: Boolean indicating if the hand is in the range
        - position: The position checked
        - action: The action checked
        - range_percentage: The total percentage of the range

    Example:
        check_hand_in_range("A5s", "BTN", "open") -> {"in_range": True, "range_percentage": 40.0, ...}
    """
    try:
        charts = GTOCharts()
        position = position.upper()

        # Validate position
        valid_positions = charts.get_positions()
        if position not in valid_positions:
            return {
                "success": False,
                "error": f"Invalid position '{position}'. Valid: {', '.join(valid_positions)}",
            }

        # Check if hand is in range
        in_range = charts.is_hand_in_range(hand, position, action)

        # Get range data for context
        range_data = charts.get_range(position, action)
        percentage = range_data.get("percentage", 0) if range_data else 0

        return {
            "success": True,
            "hand": hand.upper(),
            "position": position,
            "action": action,
            "in_range": in_range,
            "range_percentage": percentage,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# Export all tools
RANGE_TOOLS = [get_gto_range, list_available_ranges, parse_range, check_hand_in_range]
