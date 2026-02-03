# Core Module Documentation

The `src/core/` module contains all pure Python business logic for poker calculations. These functions have no UI or database dependencies and can be used from any interface.

---

## Table of Contents
1. [hand_evaluator.py](#hand_evaluatorpy) - Hand strength & equity calculation
2. [spot_analyzer.py](#spot_analyzerpy) - Comprehensive spot analysis
3. [poker_math.py](#poker_mathpy) - Pot odds, EV, SPR calculations
4. [outs_calculator.py](#outs_calculatorpy) - Drawing outs calculation
5. [gto_charts.py](#gto_chartspy) - GTO preflop ranges
6. [range_parser.py](#range_parserpy) - Range notation parsing
7. [hand_history.py](#hand_historypy) - Hand history utilities
8. [session_tracker.py](#session_trackerpy) - Session analysis

---

## hand_evaluator.py

**Purpose:** Evaluate poker hand strength and calculate equity between two hands using Monte Carlo simulation.

**Dependencies:**
- `treys` - Poker hand evaluation library

### Class: HandEvaluator

Evaluates the strength of a 5-7 card poker hand.

#### Constructor

```python
def __init__(self):
    """Initialize the hand evaluator."""
    self.evaluator = Evaluator()
```

**Library Reference:**
- [`treys.Evaluator`](https://github.com/ihendley/treys) - Core hand evaluation class

#### Method: evaluate

```python
def evaluate(self, hero_hand: str, board: str) -> Dict:
    """
    Evaluate poker hand strength.

    Args:
        hero_hand: Two cards (e.g., "As Kh")
        board: 3-5 board cards (e.g., "Qh Jh 2c")

    Returns:
        Dictionary with:
            - hand_class: str - Hand type (e.g., "Flush", "Pair")
            - rank: int - Numeric rank (1=royal flush, 7462=worst high card)
            - description: str - Human-readable description

    Raises:
        ValueError: If card format is invalid

    Example:
        >>> evaluator = HandEvaluator()
        >>> result = evaluator.evaluate("As Ks", "Qs Js Ts")
        >>> print(result['hand_class'])
        'Straight Flush'
    """
```

**Library Methods Used:**

| Method | Signature | Description |
|--------|-----------|-------------|
| `Card.new(card_str)` | `Card.new("As") -> int` | Parse card string to integer representation |
| `evaluator.evaluate(board, hand)` | `evaluate(List[int], List[int]) -> int` | Returns rank (1-7462, lower is better) |
| `evaluator.get_rank_class(rank)` | `get_rank_class(int) -> int` | Returns hand class (1-9) |
| `evaluator.class_to_string(rank_class)` | `class_to_string(int) -> str` | Returns class name |

**Hand Rank Classes (treys):**

| Class | Value | Example |
|-------|-------|---------|
| Straight Flush | 1 | A♠K♠Q♠J♠T♠ |
| Four of a Kind | 2 | A♠A♥A♦A♣K♠ |
| Full House | 3 | A♠A♥A♦K♠K♥ |
| Flush | 4 | A♠K♠Q♠J♠9♠ |
| Straight | 5 | A♠K♥Q♦J♣T♠ |
| Three of a Kind | 6 | A♠A♥A♦K♠Q♥ |
| Two Pair | 7 | A♠A♥K♠K♥Q♦ |
| Pair | 8 | A♠A♥K♠Q♥J♦ |
| High Card | 9 | A♠K♥Q♦J♣9♠ |

---

### Class: EquityCalculator

Calculates win probability between two hands using Monte Carlo simulation.

#### Method: calculate

```python
def calculate(
    self,
    hero_hand: str,
    villain_hand: str,
    board: str = "",
    iterations: int = 10000,
) -> Dict:
    """
    Calculate equity via Monte Carlo simulation.

    Args:
        hero_hand: Hero's cards (e.g., "As Kh")
        villain_hand: Villain's cards (e.g., "Qd Qc")
        board: Current board (e.g., "Ah 7s 2c"), empty for preflop
        iterations: Number of simulations (default: 10000)

    Returns:
        Dictionary with:
            - hero_equity: float - Hero's win probability (0-100)
            - villain_equity: float - Villain's win probability (0-100)
            - hero_wins: int - Number of hero wins
            - villain_wins: int - Number of villain wins
            - ties: int - Number of ties
            - iterations: int - Simulations run

    Example:
        >>> calc = EquityCalculator()
        >>> result = calc.calculate("As Ad", "Kh Kd", "", 10000)
        >>> print(f"AA vs KK: {result['hero_equity']:.1f}%")
        AA vs KK: 80.2%
    """
```

**Algorithm:**
1. Parse all known cards (hero, villain, board)
2. Create fresh deck, remove known cards
3. For each iteration:
   - Draw remaining board cards randomly
   - Evaluate both hands
   - Track wins/ties
4. Calculate equity: `(wins + ties/2) / total * 100`

**Library Methods Used:**

| Method | Signature | Description |
|--------|-----------|-------------|
| `Deck()` | `Deck() -> Deck` | Create a new 52-card deck |
| `deck.draw(n)` | `draw(int) -> List[int]` | Draw n random cards |
| `deck.cards` | `List[int]` | List of remaining cards |

---

## spot_analyzer.py

**Purpose:** Comprehensive poker situation analysis combining hand strength, equity, pot odds, SPR, and EV calculations.

**Dependencies:**
- `treys` - Card parsing
- `hand_evaluator` - Hand evaluation
- `outs_calculator` - Outs calculation
- `poker_math` - Math utilities

### Class: SpotAnalyzer

#### Method: analyze

```python
def analyze(
    self,
    hero_hand: str,
    board: str,
    pot_size: Optional[float] = None,
    bet_to_call: Optional[float] = None,
    effective_stack: Optional[float] = None,
    villain_range: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Perform comprehensive spot analysis.

    Args:
        hero_hand: Hero's cards (e.g., "As Kh")
        board: Current board cards (e.g., "Ah 7s 2c")
        pot_size: Current pot size in chips/dollars
        bet_to_call: Amount hero needs to call
        effective_stack: Effective stack size remaining
        villain_range: Villain's estimated range (optional)

    Returns:
        Dictionary containing:
            - hand_strength: Dict with class, rank, description
            - equity: float - Estimated win probability
            - outs: Dict - Breakdown by draw type
            - pot_odds: Dict - Required equity and ratio
            - implied_odds: Dict - Implied odds estimate
            - spr: float - Stack-to-pot ratio
            - ev: Dict - Expected value calculations
            - recommendation: Dict - Action with reasoning

    Example:
        >>> analyzer = SpotAnalyzer()
        >>> result = analyzer.analyze(
        ...     "Ah Kh", "Qh Jh 2c",
        ...     pot_size=100, bet_to_call=50, effective_stack=500
        ... )
        >>> print(result['recommendation']['action'])
        'CALL'
    """
```

**Analysis Pipeline:**
1. **Hand Strength** - Evaluate current hand via `HandEvaluator`
2. **Outs Calculation** - Count improving cards via `OutsCalculator`
3. **Equity Estimation** - Rule of 2/4 from outs count
4. **Pot Odds** - Calculate required equity to call
5. **Implied Odds** - Estimate future winnings potential
6. **SPR** - Stack-to-pot ratio categorization
7. **EV Calculation** - Expected value of call vs fold
8. **Recommendation** - Generate action with reasoning

---

## poker_math.py

**Purpose:** Mathematical utilities for poker calculations.

**Dependencies:** None (pure Python)

### Function: calculate_pot_odds

```python
def calculate_pot_odds(pot_size: float, bet_to_call: float) -> float:
    """
    Calculate pot odds as a percentage.

    Formula: (bet_to_call / (pot_size + bet_to_call)) * 100

    Args:
        pot_size: Current pot size
        bet_to_call: Amount required to call

    Returns:
        Required equity percentage to call profitably

    Example:
        >>> calculate_pot_odds(100, 50)
        33.33  # Need 33.33% equity to break even
    """
```

### Function: percentage_to_ratio

```python
def percentage_to_ratio(percentage: float) -> str:
    """
    Convert percentage to odds ratio format.

    Formula: (100 - percentage) / percentage

    Args:
        percentage: Pot odds as percentage

    Returns:
        Ratio string (e.g., "2.0:1")

    Example:
        >>> percentage_to_ratio(33.33)
        "2.0:1"
    """
```

### Function: estimate_implied_odds

```python
def estimate_implied_odds(
    pot_size: float,
    bet_to_call: float,
    effective_stack: float,
    outs: float,
) -> Dict[str, Any]:
    """
    Estimate implied odds based on stack and drawing potential.

    Args:
        pot_size: Current pot size
        bet_to_call: Amount to call
        effective_stack: Remaining effective stack
        outs: Number of outs

    Returns:
        Dict with:
            - percentage: float - Implied odds percentage
            - ratio: str - Ratio format
            - estimated_future_winnings: float
    """
```

### Function: categorize_spr

```python
def categorize_spr(spr: float) -> str:
    """
    Categorize stack-to-pot ratio.

    Categories:
        - SPR < 3: "low (committed)"
        - SPR 3-7: "medium"
        - SPR > 7: "high (deep)"

    Args:
        spr: Stack-to-pot ratio

    Returns:
        SPR category string
    """
```

### Function: calculate_ev

```python
def calculate_ev(
    equity: float,
    pot_size: float,
    bet_to_call: float,
    effective_stack: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Calculate expected value of calling vs folding.

    Formula: EV(call) = (equity% * pot_after_call) - ((1-equity%) * bet_to_call)

    Args:
        equity: Win equity percentage (0-100)
        pot_size: Current pot size
        bet_to_call: Amount to call
        effective_stack: Remaining stack (optional)

    Returns:
        Dict with:
            - call: float - EV of calling
            - fold: float - EV of folding (always 0)
    """
```

### Function: estimate_equity_from_outs

```python
def estimate_equity_from_outs(outs: float, board_size: int) -> float:
    """
    Estimate equity using the Rule of 2 and 4.

    Rules:
        - Flop (3 cards): equity = outs × 4
        - Turn (4 cards): equity = outs × 2
        - River (5 cards): equity = 0 (no more cards)

    Args:
        outs: Number of outs
        board_size: Number of board cards (3, 4, or 5)

    Returns:
        Estimated equity percentage (capped at 100)
    """
```

---

## outs_calculator.py

**Purpose:** Calculate drawing outs (cards that improve a hand).

**Dependencies:**
- `treys` - Card representation
- `collections.Counter` - Suit/rank counting

### Class: OutsCalculator

#### Method: calculate_outs

```python
def calculate_outs(
    self, hero_cards: List[int], board_cards: List[int]
) -> Dict[str, Any]:
    """
    Calculate outs - cards that improve the hand.

    Args:
        hero_cards: List of treys card integers for hero's hand
        board_cards: List of treys card integers for the board

    Returns:
        Dict with:
            - count: int - Total unique outs
            - breakdown: Dict - Outs by category
            - unknown_cards: int - Cards remaining in deck

    Categories in breakdown:
        - flush_draw: {count, type, suit}
        - straight_draw: {count, type, missing_ranks}
        - overcards: {count, cards}
        - pair_outs: {count, to_trips, to_two_pair}
    """
```

**Library Methods Used (treys):**

| Method | Signature | Description |
|--------|-----------|-------------|
| `Card.get_rank_int(card)` | `get_rank_int(int) -> int` | Get rank (0-12, 0=2, 12=A) |
| `Card.get_suit_int(card)` | `get_suit_int(int) -> int` | Get suit bitmask (1,2,4,8) |
| `Card.new(card_str)` | `new(str) -> int` | Parse card string |

**Suit Integer Mapping:**

| Suit | Integer | Symbol |
|------|---------|--------|
| Spades | 1 | ♠ |
| Hearts | 2 | ♥ |
| Diamonds | 4 | ♦ |
| Clubs | 8 | ♣ |

**Rank Integer Mapping:**

| Rank | Integer |
|------|---------|
| 2 | 0 |
| 3 | 1 |
| ... | ... |
| K | 11 |
| A | 12 |

#### Method: count_flush_outs

```python
def count_flush_outs(self, hero_suits, board_suits) -> Dict[str, Any]:
    """
    Count outs to make a flush.

    Rules:
        - 4 cards same suit = Flush draw (9 outs)
        - 3 cards same suit = Backdoor flush (~1 out equivalent)

    Returns:
        Dict with count, cards_needed, type, suit
    """
```

#### Method: count_straight_outs

```python
def count_straight_outs(self, hero_ranks, board_ranks) -> Dict[str, Any]:
    """
    Count outs to make a straight.

    Types detected:
        - open_ended: 8 outs (e.g., 5-6-7-8)
        - gutshot: 4 outs (e.g., 5-6-_-8-9)
        - double_gutshot: 8 outs (e.g., 4-5-_-7-_-9)
        - wheel: 4 outs (A-2-3-4 or 2-3-4-5)

    Returns:
        Dict with count, type, missing_ranks
    """
```

#### Method: count_overcard_outs

```python
def count_overcard_outs(self, hero_ranks, board_ranks) -> Dict[str, Any]:
    """
    Count outs to pair an overcard.

    Rule: Each overcard has 3 outs (4 in deck - 1 in hand)

    Returns:
        Dict with count, cards (list of overcard ranks)
    """
```

---

## gto_charts.py

**Purpose:** Load and query GTO (Game Theory Optimal) preflop ranges.

**Dependencies:**
- `json` - Range data loading
- `range_parser` - Range notation parsing
- `config` - GTO_RANGES_FILE path

### Class: GTOCharts

#### Constructor

```python
def __init__(self):
    """
    Initialize GTOCharts by loading range data from JSON.

    Data file: config.GTO_RANGES_FILE
    """
    self.data_file = GTO_RANGES_FILE
    with open(self.data_file, "r") as file:
        self.data = json.load(file)
    self.parser = RangeParser()
```

#### Method: get_positions

```python
def get_positions(self) -> List[str]:
    """
    Get list of available positions.

    Returns:
        List of position names (e.g., ["UTG", "UTG1", "MP", "LJ", "HJ", "CO", "BTN", "SB", "BB"])
    """
```

#### Method: get_actions

```python
def get_actions(self, position: str) -> List[str]:
    """
    Get available actions for a position.

    Args:
        position: Position name (e.g., "UTG", "BTN")

    Returns:
        List of action names (e.g., ["open"], ["call_vs_BTN", "3bet_vs_BTN"])
    """
```

#### Method: get_range

```python
def get_range(self, position: str, action: str) -> Optional[Dict[str, Any]]:
    """
    Get range data for a position and action.

    Args:
        position: Position name
        action: Action name

    Returns:
        Dict with:
            - hands: List[str] - Hand strings (e.g., ["AA", "KK", "AKs"])
            - notation: str - Compact notation
            - total_combos: int - Total combinations
            - percentage: float - Percentage of all hands
        None if not found
    """
```

#### Method: is_hand_in_range

```python
def is_hand_in_range(self, hand: str, position: str, action: str) -> bool:
    """
    Check if a hand is in a given range.

    Args:
        hand: Hand string (e.g., "AKs", "QQ")
        position: Position name
        action: Action name

    Returns:
        True if hand is in range
    """
```

#### Method: hands_to_matrix

```python
def hands_to_matrix(self, hands: List[str]) -> List[List[bool]]:
    """
    Convert a list of hands to a 13x13 matrix.

    Matrix layout:
        - Rows/Cols indexed by rank: A=0, K=1, Q=2, ..., 2=12
        - Diagonal (row==col): Pairs
        - Above diagonal (row<col): Suited hands
        - Below diagonal (row>col): Offsuit hands

    Args:
        hands: List of hand strings

    Returns:
        13x13 boolean matrix
    """
```

**Matrix Visual:**
```
      A    K    Q    J    T    9    8    7    6    5    4    3    2
   ┌────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┐
 A │ AA │AKs │AQs │AJs │ATs │A9s │A8s │A7s │A6s │A5s │A4s │A3s │A2s │
 K │AKo │ KK │KQs │KJs │KTs │...                                    │
 Q │AQo │KQo │ QQ │QJs │...                                         │
   ...
 2 │A2o │K2o │...                                              │ 22 │
   └────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴────┘
```

#### Method: get_matrix_hand

```python
def get_matrix_hand(self, row: int, col: int) -> str:
    """
    Get the hand string for a matrix position.

    Args:
        row: Row index (0-12)
        col: Column index (0-12)

    Returns:
        Hand string (e.g., "AA", "AKs", "AKo")
    """
```

#### Method: get_combo_count

```python
def get_combo_count(self, row: int, col: int) -> int:
    """
    Get the number of combos for a matrix position.

    Returns:
        - 6 for pairs
        - 4 for suited
        - 12 for offsuit
    """
```

### Convenience Functions

```python
def get_gto_range(position: str, action: str) -> Optional[Dict[str, Any]]:
    """Convenience function to get a GTO range."""

def get_range_matrix(position: str, action: str) -> Optional[List[List[bool]]]:
    """Convenience function to get a range as a 13x13 matrix."""
```

---

## range_parser.py

**Purpose:** Parse poker range notation into hand lists.

**Dependencies:** None (pure Python)

### Constants

```python
RANKS = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]
RANK_VALUES = {"A": 0, "K": 1, "Q": 2, ..., "2": 12}
```

### Class: RangeParser

#### Method: parse

```python
def parse(self, notation: str) -> Dict:
    """
    Parse range notation into a structured result.

    Args:
        notation: Range string like "QQ+, AKs, 98s+"

    Returns:
        Dict with:
            - hands: List[str] - Expanded hand list
            - combos: Dict - Counts by type
            - total_combos: int - Total combinations
            - percentage: float - Percentage of 1326 hands

    Example:
        >>> parser = RangeParser()
        >>> result = parser.parse("QQ+, AKs")
        >>> print(result['hands'])
        ['AA', 'KK', 'QQ', 'AKs']
    """
```

#### Method: expand_notation

```python
def expand_notation(self, element: str) -> List[str]:
    """
    Expand a single notation element.

    Supported formats:
        - Single hand: AA, AKs, AKo
        - Plus notation: QQ+, ATs+
        - Range notation: QQ-88, A5s-A2s

    Examples:
        - "QQ+" → ["AA", "KK", "QQ"]
        - "ATs+" → ["ATs", "AJs", "AQs", "AKs"]
        - "88-66" → ["88", "77", "66"]
    """
```

#### Method: count_combos

```python
def count_combos(self, hands: List[str]) -> Dict[str, int]:
    """
    Count combinations for a list of hands.

    Combo counts:
        - Pairs: 6 combos (e.g., AA = A♠A♥, A♠A♦, A♠A♣, A♥A♦, A♥A♣, A♦A♣)
        - Suited: 4 combos (e.g., AKs = A♠K♠, A♥K♥, A♦K♦, A♣K♣)
        - Offsuit: 12 combos (e.g., AKo = 4×3 combinations)

    Returns:
        Dict with: pairs, suited, offsuit, total
    """
```

---

## hand_history.py

**Purpose:** Card formatting, validation, and hand history pattern analysis.

**Dependencies:** None (pure Python)

### Constants

```python
POSITIONS = ["UTG", "UTG+1", "MP", "LJ", "HJ", "CO", "BTN", "SB", "BB"]
RESULTS = ["won", "lost", "split"]
COMMON_TAGS = ["bluff", "value", "mistake", "hero_call", "3bet", ...]
SUIT_SYMBOLS = {"s": "♠", "h": "♥", "d": "♦", "c": "♣"}
VALID_RANKS = {"2", "3", ..., "T", "J", "Q", "K", "A"}
VALID_SUITS = {"s", "h", "d", "c"}
```

### Function: format_cards

```python
def format_cards(card_string: str) -> str:
    """
    Format a card string with Unicode suit symbols.

    Args:
        card_string: Cards like "As Kh"

    Returns:
        Formatted string like "A♠ K♥"

    Example:
        >>> format_cards("As Kh")
        "A♠ K♥"
    """
```

### Function: validate_card

```python
def validate_card(card: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a single card.

    Valid format: Rank + Suit (e.g., "As", "Th", "2c")
    Ranks: 2-9, T, J, Q, K, A
    Suits: s, h, d, c

    Returns:
        Tuple of (is_valid, error_message)
    """
```

### Function: validate_hero_hand

```python
def validate_hero_hand(hand: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a hero hand (must be exactly 2 cards).

    Returns:
        Tuple of (is_valid, error_message)
    """
```

### Function: validate_board

```python
def validate_board(board: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a board (must be 0, 3, 4, or 5 cards).

    Returns:
        Tuple of (is_valid, error_message)
    """
```

### Function: validate_hand_and_board

```python
def validate_hand_and_board(hero_hand: str, board: str) -> Tuple[bool, Optional[str]]:
    """
    Validate hero hand and board together (no duplicates).

    Returns:
        Tuple of (is_valid, error_message)
    """
```

### Function: suggest_tags

```python
def suggest_tags(
    action_summary: Optional[str] = None,
    result: Optional[str] = None,
    hero_hand: Optional[str] = None,
) -> List[str]:
    """
    Suggest tags based on action summary, result, and hand.

    Detects keywords like:
        - "bluff", "c-bet", "3bet" → corresponding tags
        - Pocket pairs → "pocket_pair", "set_mining"
        - Suited connectors → "suited_connector"

    Returns:
        List of suggested tag strings
    """
```

### Function: format_board_by_street

```python
def format_board_by_street(board: str) -> Dict[str, str]:
    """
    Format a board by street (flop, turn, river).

    Args:
        board: Full board like "Qh Jh 2c 5d 9s"

    Returns:
        Dict with:
            - flop: str (formatted first 3 cards)
            - turn: str (formatted 4th card)
            - river: str (formatted 5th card)
    """
```

### Function: analyze_hand_patterns

```python
def analyze_hand_patterns(hands: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze patterns in a list of hands.

    Returns:
        Dict with:
            - position_win_rates: Dict[str, float]
            - tag_win_rates: Dict[str, float]
            - bluff_success_rate: float
            - value_bet_win_rate: float
            - street_distribution: Dict[str, float]
            - insights: List[str] - Auto-generated insights
    """
```

---

## session_tracker.py

**Purpose:** Bankroll analysis, variance calculations, and session statistics.

**Dependencies:**
- `math` - Square root for standard deviation
- `plotext` - ASCII graph generation

### Function: calculate_variance

```python
def calculate_variance(profits: List[float]) -> float:
    """
    Calculate the variance of session profits.

    Formula: Σ(x - mean)² / (n - 1)

    Args:
        profits: List of session profit/loss values

    Returns:
        Variance value (sample variance)
    """
```

### Function: calculate_standard_deviation

```python
def calculate_standard_deviation(profits: List[float]) -> float:
    """
    Calculate standard deviation of session profits.

    Formula: √variance

    Returns:
        Standard deviation (0 if insufficient data)
    """
```

### Function: calculate_sharpe_ratio

```python
def calculate_sharpe_ratio(
    profits: List[float],
    risk_free_rate: float = 0.0,
) -> float:
    """
    Calculate Sharpe ratio for risk-adjusted returns.

    Formula: (mean_profit - risk_free_rate) / std_dev

    Returns:
        Sharpe ratio (0 if insufficient data)
    """
```

### Function: calculate_max_drawdown

```python
def calculate_max_drawdown(cumulative_profits: List[float]) -> Dict[str, float]:
    """
    Calculate maximum drawdown from peak.

    Returns:
        Dict with:
            - max_drawdown: float - Dollar amount of max drawdown
            - max_drawdown_pct: float - Percentage from peak
            - peak: float - Peak value
            - trough: float - Trough value
    """
```

### Function: analyze_bankroll_health

```python
def analyze_bankroll_health(
    current_bankroll: float,
    stake_big_blind: float,
    sessions: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Analyze bankroll health and provide recommendations.

    Args:
        current_bankroll: Current total bankroll
        stake_big_blind: Big blind for the stake being played
        sessions: List of session data dicts

    Returns:
        Dict with:
            - buyins_available: float
            - risk_of_ruin: float
            - health_status: str ("excellent", "good", "caution", "critical")
            - recommended_stakes: List[str]
            - recommendations: List[str]
    """
```

### Function: calculate_streak_info

```python
def calculate_streak_info(profits: List[float]) -> Dict[str, Any]:
    """
    Calculate winning/losing streak information.

    Returns:
        Dict with:
            - current_streak: int
            - current_streak_type: str ("win", "loss", "none")
            - longest_win_streak: int
            - longest_loss_streak: int
    """
```

### Function: generate_ascii_graph

```python
def generate_ascii_graph(
    data_points: List[Dict[str, Any]],
    width: int = 80,
    height: int = 15,
) -> List[str]:
    """
    Generate a graph for bankroll progression using plotext.

    Args:
        data_points: List of dicts with 'date' and 'cumulative' keys
        width: Width of the graph in characters
        height: Height of the graph in characters

    Returns:
        List of strings representing the graph lines
    """
```

**Library Reference (plotext):**

| Method | Signature | Description |
|--------|-----------|-------------|
| `plt.clear_figure()` | `clear_figure()` | Clear previous plot |
| `plt.plot_size(w, h)` | `plot_size(int, int)` | Set plot dimensions |
| `plt.plot(x, y, marker)` | `plot(List, List, str)` | Plot line |
| `plt.hline(y)` | `hline(float)` | Add horizontal line |
| `plt.title(text)` | `title(str)` | Set plot title |
| `plt.xlabel(text)` | `xlabel(str)` | Set x-axis label |
| `plt.ylabel(text)` | `ylabel(str)` | Set y-axis label |
| `plt.build()` | `build() -> str` | Build plot as string |
| `plt.uncolorize(text)` | `uncolorize(str) -> str` | Remove ANSI codes |

**Official Documentation:** [plotext on GitHub](https://github.com/piccolomo/plotext)

---

## Summary

The core module provides:

| File | Primary Purpose | Key Classes/Functions |
|------|-----------------|----------------------|
| `hand_evaluator.py` | Hand strength & equity | `HandEvaluator`, `EquityCalculator` |
| `spot_analyzer.py` | Full spot analysis | `SpotAnalyzer.analyze()` |
| `poker_math.py` | Math utilities | `calculate_pot_odds()`, `calculate_ev()` |
| `outs_calculator.py` | Drawing outs | `OutsCalculator.calculate_outs()` |
| `gto_charts.py` | GTO ranges | `GTOCharts.get_range()` |
| `range_parser.py` | Range notation | `RangeParser.parse()` |
| `hand_history.py` | Card utilities | `format_cards()`, `validate_hand_and_board()` |
| `session_tracker.py` | Bankroll analysis | `analyze_bankroll_health()`, `generate_ascii_graph()` |

All functions in this module are pure Python with no UI dependencies, making them suitable for use in any interface (TUI, API, mobile).
