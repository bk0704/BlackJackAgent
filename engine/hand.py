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
            total -= 10
            aces_counted_as_11 -= 1
        self.total = total
        self.aces_counted_as_11 = aces_counted_as_11
        self.update_is_soft()
        self.update_is_bust()

    def update_is_soft(self):
        self.is_soft = self.aces_counted_as_11 > 0

    def update_is_bust(self):
        self.is_bust = self.total > 21

    def check_natural_blackjack(self):
        return len(self.cards) == 2 and self.total == 21