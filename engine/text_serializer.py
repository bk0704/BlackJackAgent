def serialize_state(game_state, template="A"):
    cards_str = ", ".join(str(c) for c in game_state.player_hand.cards)
    hand_type = "soft" if game_state.is_soft else "hard"
    t = game_state.player_total
    d = game_state.dealer_visible_card

    if template == "A":
        return (
            f"Your hand: {cards_str} (total: {t}, {hand_type})\n"
            f"Dealer showing: {d}\n"
            f"What do you do? Hit or Stand?"
        )
    elif template == "B":
        return (
            f"You're holding {cards_str} for a total of {t} ({hand_type}). "
            f"The dealer is showing a {d}. Hit or Stand?"
        )
    elif template == "C":
        soft_str = "Yes" if game_state.is_soft else "No"
        return (
            f"Hand: {cards_str} | Total: {t} | Soft: {soft_str} | Dealer upcard: {d}\n"
            f"Your action?"
        )