import pytest
from engine.deck import Deck


def test_deck_has_52_cards():
    deck = Deck()
    assert len(deck.cards) == 52


def test_deck_card_counts():
    deck = Deck()
    counts = {}
    for card in deck.cards:
        counts[card] = counts.get(card, 0) + 1

    for n in range(2, 11):
        assert counts[n] == 4, f"{n} appears {counts[n]} times, expected 4"

    for face in ('J', 'Q', 'K'):
        assert counts[face] == 4, f"{face} appears {counts[face]} times, expected 4"

    assert counts['A'] == 4, f"A appears {counts['A']} times, expected 4"


def test_reshuffle_triggers_below_15():
    deck = Deck()
    # Draw down to 14 cards (just below the 15-card threshold)
    for _ in range(38):
        deck.draw()
    assert len(deck.cards) == 14

    # This draw should trigger a rebuild: deck resets to 52 then pops 1
    deck.draw()
    assert len(deck.cards) == 51
