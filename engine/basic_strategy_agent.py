def _card_to_value(card):
    if card in ('J', 'Q', 'K'):
        return 10
    if card == 'A':
        return 11
    return card


_DEALERS = range(2, 12)  # 2-10 and 11 (ace)

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
    def act(self, game_state):
        total = game_state.player_total
        dealer_val = _card_to_value(game_state.dealer_visible_card)
        table = _SOFT if game_state.is_soft else _HARD
        return table.get((total, dealer_val), "stand")
