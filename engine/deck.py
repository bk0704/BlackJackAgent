import random

class Deck:
    """
    Represents the whole blackjack deck

    Att
    """
    def __init__(self):
        numbered = list(range(2, 11))
        face = ['J', 'Q', 'K']
        ace = ['A']
        self.cards = (numbered + face + ace) * 4
    def shuffle(self):
        random.shuffle(self.cards)
    def draw(self):
        if len(self.cards) < 15:
            self.__init__()
            self.shuffle()
        return self.cards.pop()
    
