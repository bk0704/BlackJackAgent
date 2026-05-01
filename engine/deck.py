import random

CARD_VALUES = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 'A']

class Deck:
    def __init__(self):
        self.cards = CARD_VALUES * 4
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self):
        if not self.cards:
            raise IndexError("Cannot draw from an empty deck")
        return self.cards.pop()
