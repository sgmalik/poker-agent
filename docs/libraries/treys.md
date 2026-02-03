# treys Library Reference

## Overview

**treys** is a Python library for fast poker hand evaluation. It provides efficient algorithms for evaluating 5-7 card poker hands and comparing hand strengths.

**Official Repository:** https://github.com/ihendley/treys

**Installation:**
```bash
pip install treys
```

---

## Core Classes

### Class: `Card`

Represents a playing card using a compact integer encoding.

**Import:**
```python
from treys import Card
```

#### Static Method: `Card.new(card_string)`

Creates a card from a string representation.

```python
Card.new(card_string: str) -> int
```

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `card_string` | `str` | Card notation: rank + suit |

**Card Notation:**
- Ranks: `2`, `3`, `4`, `5`, `6`, `7`, `8`, `9`, `T`, `J`, `Q`, `K`, `A`
- Suits: `s` (spades), `h` (hearts), `d` (diamonds), `c` (clubs)

**Returns:**
| Type | Description |
|------|-------------|
| `int` | Integer representation of the card |

**Examples:**
```python
from treys import Card

ace_spades = Card.new("As")      # Ace of spades
king_hearts = Card.new("Kh")     # King of hearts
ten_diamonds = Card.new("Td")    # Ten of diamonds
two_clubs = Card.new("2c")       # Two of clubs
```

---

#### Static Method: `Card.int_to_str(card_int)`

Converts integer card representation back to string.

```python
Card.int_to_str(card_int: int) -> str
```

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `card_int` | `int` | Integer card value |

**Returns:**
| Type | Description |
|------|-------------|
| `str` | Card string (e.g., "As") |

**Example:**
```python
card_int = Card.new("As")
card_str = Card.int_to_str(card_int)  # "As"
```

---

#### Static Method: `Card.print_pretty_card(card_int)`

Returns a pretty-printed card string with Unicode suits.

```python
Card.print_pretty_card(card_int: int) -> str
```

**Returns:**
| Type | Description |
|------|-------------|
| `str` | Pretty card string (e.g., "A♠") |

**Example:**
```python
card = Card.new("Kh")
pretty = Card.print_pretty_card(card)  # "K♥"
```

---

#### Static Method: `Card.print_pretty_cards(card_ints)`

Returns pretty-printed cards for a list.

```python
Card.print_pretty_cards(card_ints: List[int]) -> str
```

**Returns:**
| Type | Description |
|------|-------------|
| `str` | Space-separated pretty cards |

**Example:**
```python
hand = [Card.new("As"), Card.new("Kh")]
pretty = Card.print_pretty_cards(hand)  # "A♠ K♥"
```

---

### Class: `Evaluator`

Evaluates poker hands and compares hand strengths.

**Import:**
```python
from treys import Evaluator
```

#### Constructor

```python
Evaluator()
```

No parameters required. Creates a new evaluator instance.

---

#### Method: `evaluate(cards, board)`

Evaluates a poker hand (5-7 cards total).

```python
evaluator.evaluate(cards: List[int], board: List[int]) -> int
```

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `cards` | `List[int]` | Hole cards (2 cards) |
| `board` | `List[int]` | Community cards (3-5 cards) |

**Returns:**
| Type | Description |
|------|-------------|
| `int` | Hand rank (1 = Royal Flush, 7462 = worst high card) |

**Rank Ranges:**
| Hand Class | Rank Range |
|------------|------------|
| Straight Flush | 1 - 10 |
| Four of a Kind | 11 - 166 |
| Full House | 167 - 322 |
| Flush | 323 - 1599 |
| Straight | 1600 - 1609 |
| Three of a Kind | 1610 - 2467 |
| Two Pair | 2468 - 3325 |
| One Pair | 3326 - 6185 |
| High Card | 6186 - 7462 |

**Example:**
```python
from treys import Evaluator, Card

evaluator = Evaluator()

# Pocket aces on a board
hand = [Card.new("As"), Card.new("Ad")]
board = [Card.new("Ah"), Card.new("Kd"), Card.new("2c")]

rank = evaluator.evaluate(hand, board)  # Returns rank integer
```

---

#### Method: `class_to_string(hand_rank)`

Converts a hand rank to its class name.

```python
evaluator.class_to_string(hand_rank: int) -> str
```

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `hand_rank` | `int` | Hand rank from `evaluate()` |

**Returns:**
| Type | Description |
|------|-------------|
| `str` | Hand class name |

**Possible Return Values:**
- `"Straight Flush"`
- `"Four of a Kind"`
- `"Full House"`
- `"Flush"`
- `"Straight"`
- `"Three of a Kind"`
- `"Two Pair"`
- `"Pair"`
- `"High Card"`

**Example:**
```python
rank = evaluator.evaluate(hand, board)
hand_class = evaluator.class_to_string(rank)  # "Three of a Kind"
```

---

#### Method: `get_rank_class(hand_rank)`

Gets the numeric class of a hand rank.

```python
evaluator.get_rank_class(hand_rank: int) -> int
```

**Returns:**
| Value | Hand Class |
|-------|------------|
| 1 | Straight Flush |
| 2 | Four of a Kind |
| 3 | Full House |
| 4 | Flush |
| 5 | Straight |
| 6 | Three of a Kind |
| 7 | Two Pair |
| 8 | Pair |
| 9 | High Card |

---

### Class: `Deck`

Represents a standard 52-card deck.

**Import:**
```python
from treys import Deck
```

#### Constructor

```python
Deck()
```

Creates a new shuffled deck.

---

#### Method: `draw(n)`

Draws cards from the deck.

```python
deck.draw(n: int) -> List[int]
```

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `n` | `int` | Number of cards to draw |

**Returns:**
| Type | Description |
|------|-------------|
| `List[int]` | List of card integers |

**Example:**
```python
from treys import Deck

deck = Deck()
hand = deck.draw(2)      # Draw 2 hole cards
board = deck.draw(5)     # Draw 5 community cards
```

---

#### Method: `shuffle()`

Shuffles the deck (restores all cards).

```python
deck.shuffle() -> None
```

---

## Usage in Poker Coach Agent

### Card Parsing (hand_evaluator.py)

```python
from treys import Card

def parse_cards(card_string: str) -> List[int]:
    """Parse space-separated card notation."""
    cards = []
    for card in card_string.split():
        cards.append(Card.new(card.strip()))
    return cards

# Usage
hand = parse_cards("As Kh")  # [integer, integer]
board = parse_cards("Qh Jh 2c")
```

### Hand Evaluation (hand_evaluator.py)

```python
from treys import Evaluator, Card

class HandEvaluator:
    def __init__(self):
        self._evaluator = Evaluator()

    def evaluate(self, hero_hand: str, board: str) -> dict:
        hand_cards = self._parse_cards(hero_hand)
        board_cards = self._parse_cards(board)

        rank = self._evaluator.evaluate(hand_cards, board_cards)
        hand_class = self._evaluator.class_to_string(rank)

        return {
            "rank": rank,
            "hand_class": hand_class,
            "description": self._get_description(rank, hand_class),
        }
```

### Equity Calculation (hand_evaluator.py)

```python
from treys import Deck, Evaluator, Card

class EquityCalculator:
    def __init__(self):
        self._evaluator = Evaluator()

    def calculate(self, hero: str, villain: str, board: str, iterations: int) -> dict:
        hero_cards = self._parse_cards(hero)
        villain_cards = self._parse_cards(villain)
        board_cards = self._parse_cards(board) if board else []

        used_cards = set(hero_cards + villain_cards + board_cards)
        hero_wins = 0
        villain_wins = 0
        ties = 0

        for _ in range(iterations):
            # Build remaining deck
            deck = Deck()
            deck.cards = [c for c in deck.cards if c not in used_cards]

            # Complete the board
            remaining = 5 - len(board_cards)
            run_board = board_cards + deck.draw(remaining)

            # Evaluate both hands
            hero_rank = self._evaluator.evaluate(hero_cards, run_board)
            villain_rank = self._evaluator.evaluate(villain_cards, run_board)

            # Lower rank wins
            if hero_rank < villain_rank:
                hero_wins += 1
            elif villain_rank < hero_rank:
                villain_wins += 1
            else:
                ties += 1

        return {
            "hero_equity": hero_wins / iterations * 100,
            "villain_equity": villain_wins / iterations * 100,
            "hero_wins": hero_wins,
            "villain_wins": villain_wins,
            "ties": ties,
        }
```

---

## Important Notes

### Card Format
- Always use 2-character notation: rank + suit
- Ranks are case-insensitive for input but standardized internally
- Ten is represented as `T`, not `10`

### Rank Interpretation
- **Lower rank = better hand**
- Rank 1 = Royal Flush (best)
- Rank 7462 = 7-5-4-3-2 offsuit high card (worst)

### Performance
- treys uses lookup tables for O(1) evaluation
- Monte Carlo simulations can run thousands of iterations quickly
- For equity calculations, 10,000 iterations provides good accuracy

### Common Errors

```python
# Wrong: Using "10" instead of "T"
Card.new("10s")  # Raises KeyError

# Correct: Use "T" for ten
Card.new("Ts")   # Works

# Wrong: Invalid suit
Card.new("Ax")   # Raises KeyError

# Correct: Use s, h, d, or c
Card.new("As")   # Works
```
