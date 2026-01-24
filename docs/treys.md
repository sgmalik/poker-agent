# Treys Library Reference

Treys is a fast poker hand evaluation library. It uses integer representations for cards and bitwise operations for speed.

## Card Representation

Cards are integers. Create them with `Card.new(rank_suit_string)`:

```python
from treys import Card

ace_spades = Card.new('As')  # Ace of spades
king_hearts = Card.new('Kh')  # King of hearts
ten_clubs = Card.new('Tc')   # Ten of clubs (use 'T' not '10')
two_diamonds = Card.new('2d')
```

**Ranks:** `A K Q J T 9 8 7 6 5 4 3 2`
**Suits:** `s h d c` (spades, hearts, diamonds, clubs)

### Printing Cards

```python
Card.print_pretty_card(card)        # Single card: [ A♠ ]
Card.print_pretty_cards([c1, c2])   # Multiple cards
Card.int_to_str(card)               # Returns "As" string
```

## Hand Evaluation

The `Evaluator` ranks hands from 1 (best) to 7462 (worst).

```python
from treys import Evaluator

evaluator = Evaluator()

# Evaluate 5-card hand (no board)
hand = [Card.new('As'), Card.new('Ks'), Card.new('Qs'), Card.new('Js'), Card.new('Ts')]
rank = evaluator.evaluate([], hand)  # Empty board, 5-card hand

# Evaluate with board (Texas Hold'em style)
board = [Card.new('Ah'), Card.new('Kd'), Card.new('5c')]
hole = [Card.new('As'), Card.new('Ks')]
rank = evaluator.evaluate(board, hole)  # Returns integer rank
```

### Rank Values

| Rank Range | Hand Type |
|------------|-----------|
| 1 | Royal Flush |
| 2-10 | Straight Flush |
| 11-166 | Four of a Kind |
| 167-322 | Full House |
| 323-1599 | Flush |
| 1600-1609 | Straight |
| 1610-2467 | Three of a Kind |
| 2468-3325 | Two Pair |
| 3326-6185 | One Pair |
| 6186-7462 | High Card |

### Getting Hand Class

```python
rank = evaluator.evaluate(board, hole)

# Get hand class (0-8)
hand_class = evaluator.get_rank_class(rank)

# Get string description
class_string = evaluator.class_to_string(hand_class)  # "Flush", "Two Pair", etc.

# Hand class constants
evaluator.MAX_STRAIGHT_FLUSH  # 10
evaluator.MAX_FOUR_OF_A_KIND  # 166
evaluator.MAX_FULL_HOUSE      # 322
evaluator.MAX_FLUSH           # 1599
evaluator.MAX_STRAIGHT        # 1609
evaluator.MAX_THREE_OF_A_KIND # 2467
evaluator.MAX_TWO_PAIR        # 3325
evaluator.MAX_PAIR            # 6185
evaluator.MAX_HIGH_CARD       # 7462
```

## Deck Operations

```python
from treys import Deck

deck = Deck()
deck.shuffle()

# Draw cards
card = deck.draw(1)       # Returns single card int
cards = deck.draw(5)      # Returns list of 5 cards

# Check remaining
remaining = len(deck.cards)
```

## Common Patterns

### Check if hand beats another

```python
rank1 = evaluator.evaluate(board, hand1)
rank2 = evaluator.evaluate(board, hand2)
# Lower rank = better hand
winner = hand1 if rank1 < rank2 else hand2
```

### Calculate equity (Monte Carlo)

```python
def calculate_equity(hole_cards, board, num_simulations=1000):
    """Estimate win probability against random opponent."""
    evaluator = Evaluator()
    wins = 0

    for _ in range(num_simulations):
        deck = Deck()
        # Remove known cards from deck
        for card in hole_cards + board:
            deck.cards.remove(card)

        # Complete board if needed
        remaining = 5 - len(board)
        full_board = board + deck.draw(remaining)

        # Draw opponent hand
        opp_hand = deck.draw(2)

        hero_rank = evaluator.evaluate(full_board, hole_cards)
        opp_rank = evaluator.evaluate(full_board, opp_hand)

        if hero_rank < opp_rank:
            wins += 1
        elif hero_rank == opp_rank:
            wins += 0.5

    return wins / num_simulations
```

### Parse hand string to cards

```python
def parse_hand(hand_str: str) -> list:
    """Parse 'As Kh' or 'AsKh' to card list."""
    hand_str = hand_str.replace(' ', '')
    cards = []
    for i in range(0, len(hand_str), 2):
        cards.append(Card.new(hand_str[i:i+2]))
    return cards
```

## Key Points

- Cards are integers, not objects
- Lower evaluation rank = stronger hand
- Board can be 0-5 cards, hole cards are 2
- `evaluate()` always finds best 5-card hand from available cards
- Evaluator is stateless, create once and reuse
