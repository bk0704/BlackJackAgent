class Hand:
    def __init__(self):
        self.cards = []
        self.total = 0
        self.aces_counted_as_11 = 0
        self.is_soft = False
        self.is_bust = False
        self.is_natural_blackjack = False

    def add_card(self, card):
        self.cards.append(card)

    def calculate_total(self):
        sum_non = sum(10 if card in ('J', 'Q', 'K') else card for card in self.cards if card != 'A')
        aces_counted_as_11 = sum(1 for card in self.cards if card == 'A')
        total = sum_non + (aces_counted_as_11 * 11)
        while total > 21 and aces_counted_as_11 > 0:
            total = total - 10
            aces_counted_as_11 = aces_counted_as_11 - 1
        self.total = total
        self.aces_counted_as_11 = aces_counted_as_11

    def is_soft(self):
        is_soft = self.aces_counted_as_11 > 0
        self.is_soft = is_soft

    # TODO: Implement is_bust()
    def is_bust(self):
        is_bust = self.total > 21
        self.is_bust = is_bust

    # TODO: Implement is_natural_blackjack
    def is_natural_blackjack(self):
        is_len_2 = len(self.cards) == 2
        is_21 = self.total == 21
        return is_len_2 and is_21