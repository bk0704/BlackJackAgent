def serialize_state(game_state):
    cards_str = ", ".join(str(c) for c in game_state.player_hand.cards)
    hand_type = "soft" if game_state.is_soft else "hard"
    lines = [
        f"Your hand: {cards_str} (total: {game_state.player_total}, {hand_type})",
        f"Dealer showing: {game_state.dealer_visible_card}",
    ]
    if game_state.available_actions:
        actions = " or ".join(a.capitalize() for a in game_state.available_actions)
        lines.append(f"What do you do? {actions}?")
    return "\n".join(lines)
