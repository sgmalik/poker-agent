  Different Equity Metrics for Made Hands

  Current Implementation (Outs-Based Equity):
  - Works by counting cards that improve your hand
  - Perfect for drawing hands: flush draws (9 outs), straight draws (8 outs), overcards (6 outs)
  - Fails for made hands: A set has only ~7 outs to boat/quads, showing low equity despite being strong

  Alternative Metrics for Made Hands:

  1. Hand Percentile (Relative Hand Strength)

  - What it is: Where your hand ranks among all possible holdings
  - Example: Top set on As Ks Qc is top 2% of hands
  - Implementation: Enumerate all 1,326 possible hole card combinations, evaluate each against the board, rank yours
  - Use case: "I have top 5% hand, villain is betting - are they bluffing or do they have me beat?"

  2. Board Texture Vulnerability Score

  - What it is: How vulnerable your made hand is to draws
  - Factors:
    - Flush draws possible? (2+ suited cards on board)
    - Straight draws possible? (connected cards)
    - How many overcards to your pair?
  - Example: Top pair on a rainbow board (low vulnerability) vs top pair on Kh Qh Jd (high vulnerability)
  - Use case: "Should I bet for value or protection?"

  3. Minimum Defense Frequency (MDF)

  - What it is: GTO concept - how often you need to call to prevent villain from auto-profiting with any two cards
  - Formula: MDF = pot / (pot + bet)
  - Example: Villain bets 50 into 100, MDF = 100/(100+50) = 66.67% - you need to defend 67% of your range
  - Use case: "Am I in the defending portion of my range?"

  4. Range-Based Equity (The Proper Solution)

  - What it is: Your win probability vs villain's perceived range
  - Example: You have AhAd on AsKhQc, villain's range is {QQ+, AK, KQ}
    - Monte Carlo simulation: your AAA vs each hand in range
    - Weighted average based on range frequencies
  - Implementation:
  villain_range = ["QQ", "KK", "AK", "KQ"]  # Parse range notation
  for hand in villain_range:
      equity_vs_hand = run_monte_carlo(hero, villain_hand, board)
  weighted_equity = average(all_equities)
  - Use case: This is THE solution for made hands - you're not drawing, you're evaluating vs what villain likely has

  What I Recommend:
  Start with Range-Based Equity (option 4) as the proper solution for made hands. The other three are supplementary tools that give additional context. When villain_range parameter is provided, use Monte Carlo against that range instead of
   outs-based estimation.

