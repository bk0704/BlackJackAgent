class GameState:
    def __init__(self, player_hand, player_total, is_soft, dealer_visible_card, available_actions):
        self.player_hand = player_hand
        self.player_total = player_total
        self.is_soft = is_soft
        self.dealer_visible_card = dealer_visible_card
        self.available_actions = available_actions