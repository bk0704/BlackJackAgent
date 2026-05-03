# Game
# ============================================================
# Owns the full flow of a single hand.
# Coordinates all other classes.
# Only reset(), step(), and get_state() are public.
# Everything else is internal.
#
# Attributes
# ----------
# deck                 Deck instance
# player_hand          Hand instance
# dealer_hand          Hand instance
# is_terminal          Whether the current game has ended (bool)
# reward               Current reward, starts at 0
#
# Public Methods
# --------------
# reset()
#   - Draws 4 cards, 2 to player, 2 to dealer
#   - Checks for natural blackjack on both sides immediately
#   - Returns initial GameState
#
# step(action)
#   - Accepts "hit" or "stand" from the agent
#   - If hit:
#       - Draw a card, add to player hand
#       - If bust: reward = -1, is_terminal = True, return final GameState
#       - If not bust: return updated GameState, reward = 0, is_terminal = False
#   - If stand:
#       - Run dealer turn automatically
#       - Resolve outcome
#       - Return final GameState
#
# get_state()
#   - Packages current internal state into a GameState object
#   - Returns GameState
#   - Can be called at any point during the game
#
# Internal Methods
# ----------------
# _deal()
#   - Draws opening cards and distributes them
#
# _check_natural_blackjack()
#   - Runs immediately after deal
#   - Player BJ, dealer no BJ  → reward = +1, terminal
#   - Dealer BJ, player no BJ  → reward = -1, terminal
#   - Both BJ                  → reward =  0, terminal
#   - Neither                  → continue to player turn
#
# _run_dealer_turn()
#   - Runs after player stands, no agent input
#   - Hit while dealer total <= 16
#   - Stand when dealer total >= 17
#
# _resolve_outcome()
#   - Dealer bust              → reward = +1
#   - Player total higher      → reward = +1
#   - Dealer total higher      → reward = -1
#   - Equal totals             → reward =  0
#
# Reward Structure
# ----------------
# Win  → +1.0
# Loss → -1.0
# Draw →  0.0
# ============================================================

from engine.deck import Deck
from engine.hand import Hand
from engine.gameState import GameState as _GameStateOuter
GameState = _GameStateOuter.GameState


class Game:
    def __init__(self):
        self.deck = Deck()
        self.player_hand = Hand()
        self.dealer_hand = Hand()
        self.is_terminal = False
        self.reward = 0

    def reset(self):
        self.player_hand = Hand()
        self.dealer_hand = Hand()
        self.is_terminal = False
        self.reward = 0
        self.deck.shuffle()
        self._deal()
        self._check_natural_blackjack()
        return self.get_state()

    def step(self, action):
        if action == "hit":
            self.player_hand.add_card(self.deck.draw())
            self.player_hand.calculate_total()
            if self.player_hand.total > 21:
                self.reward = -1
                self.is_terminal = True
        elif action == "stand":
            self._run_dealer_turn()
            self._resolve_outcome()
        return self.get_state()

    def get_state(self):
        return GameState(
            player_hand=self.player_hand,
            player_total=self.player_hand.total,
            is_soft=self.player_hand.aces_counted_as_11 > 0,
            dealer_visible_card=self.dealer_hand.cards[0],
            available_actions=[] if self.is_terminal else ["hit", "stand"],
        )

    def _deal(self):
        self.player_hand.add_card(self.deck.draw())
        self.dealer_hand.add_card(self.deck.draw())
        self.player_hand.add_card(self.deck.draw())
        self.dealer_hand.add_card(self.deck.draw())
        self.player_hand.calculate_total()
        self.dealer_hand.calculate_total()

    def _check_natural_blackjack(self):
        player_bj = len(self.player_hand.cards) == 2 and self.player_hand.total == 21
        dealer_bj = len(self.dealer_hand.cards) == 2 and self.dealer_hand.total == 21
        if player_bj and not dealer_bj:
            self.reward = 1
            self.is_terminal = True
        elif dealer_bj and not player_bj:
            self.reward = -1
            self.is_terminal = True
        elif player_bj and dealer_bj:
            self.reward = 0
            self.is_terminal = True

    def _run_dealer_turn(self):
        while self.dealer_hand.total <= 16:
            self.dealer_hand.add_card(self.deck.draw())
            self.dealer_hand.calculate_total()

    def _resolve_outcome(self):
        if self.dealer_hand.total > 21:
            self.reward = 1
        elif self.player_hand.total > self.dealer_hand.total:
            self.reward = 1
        elif self.dealer_hand.total > self.player_hand.total:
            self.reward = -1
        else:
            self.reward = 0
        self.is_terminal = True