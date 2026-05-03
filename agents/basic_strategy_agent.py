def _card_to_value(card):
    """Convert a card face value to its numeric blackjack value.

    Face cards (J, Q, K) are worth 10. Aces are treated as 11 here since
    soft/hard distinction is already handled upstream by game_state.is_soft.
    Numeric cards are returned as-is (already integers).
    """
    if card in ('J', 'Q', 'K'):
        return 10
    if card == 'A':
        return 11
    return card


_DEALERS = range(2, 12)  # 2-10 and 11 (ace)

# ---------------------------------------------------------------------------
# Hard totals lookup table: (player_total, dealer_upcard) -> "hit" | "stand"
#
# Built from standard basic strategy charts:
#   - Hard 4-11:  always hit (can't bust, and doubling not modeled yet)
#   - Hard 12:    stand only vs dealer 4/5/6 (dealer bust-prone range)
#   - Hard 13-16: stand vs dealer 2-6, hit vs 7+ (dealer strong upcards)
#   - Hard 17-21: always stand
# ---------------------------------------------------------------------------
_HARD = {}
for _t in range(4, 12):
    for _d in _DEALERS:
        _HARD[(_t, _d)] = "hit"
for _d in _DEALERS:
    _HARD[(12, _d)] = "stand" if _d in (4, 5, 6) else "hit"
for _t in range(13, 17):
    for _d in _DEALERS:
        _HARD[(_t, _d)] = "stand" if _d in (2, 3, 4, 5, 6) else "hit"
for _t in range(17, 22):
    for _d in _DEALERS:
        _HARD[(_t, _d)] = "stand"

# ---------------------------------------------------------------------------
# Soft totals lookup table: (player_total, dealer_upcard) -> "hit" | "stand"
#
# A "soft" total contains an Ace counted as 11, so the player can't bust on
# a single hit. Built from standard basic strategy charts:
#   - Soft 12-17: always hit (flexible hand; improve without bust risk)
#   - Soft 18:    stand vs dealer 2-8, hit vs 9/10/A (dealer too strong)
#   - Soft 19-21: always stand
# ---------------------------------------------------------------------------
_SOFT = {}
for _t in range(12, 18):  # soft 12 (A+A) through soft 17 (A+6)
    for _d in _DEALERS:
        _SOFT[(_t, _d)] = "hit"
for _d in _DEALERS:
    _SOFT[(18, _d)] = "hit" if _d in (9, 10, 11) else "stand"
for _t in range(19, 22):
    for _d in _DEALERS:
        _SOFT[(_t, _d)] = "stand"


class BasicStrategyAgent:
    """Blackjack agent that plays according to standard basic strategy.

    Basic strategy is the mathematically optimal set of hit/stand decisions
    based solely on the player's total and the dealer's visible upcard. It
    assumes a freshly shuffled multi-deck shoe and no card counting.

    Decisions are pre-computed into two lookup tables (_HARD, _SOFT) at
    module load time for O(1) lookups at runtime.

    Note: doubles and splits are not modeled — only hit/stand decisions.
    """

    def act(self, game_state):
        """Return the basic-strategy action for the current game state.

        Selects the soft or hard lookup table based on whether the player's
        hand is soft, then returns the recommended action for the
        (player_total, dealer_upcard) pair. Falls back to "stand" for any
        total not covered by the tables (e.g. a busted hand).

        Args:
            game_state: object exposing player_total (int), dealer_visible_card
                        (int | str), and is_soft (bool).

        Returns:
            "hit" or "stand"
        """
        total = game_state.player_total
        dealer_val = _card_to_value(game_state.dealer_visible_card)
        table = _SOFT if game_state.is_soft else _HARD
        return table.get((total, dealer_val), "stand")
