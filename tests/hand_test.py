import pytest
from engine.hand import Hand

# Hand              Expected Total    Soft?    Bust?    Natural BJ?
# ----------------------------------------------------------------
# A + 5             16                Yes      No       No
# A + K             21                Yes      No       Yes
# A + A             12                Yes      No       No
# A + A + 9         21                Yes      No       No
# A + A + K         12                No       No       No
# 9 + 6             15                No       No       No
# K + Q             20                No       No       No
# 7 + 8 + 9         24                No       Yes      No
# A + 9 + 5         15                No       No       No
# 5 + 5 + A         21                Yes      No       No


def make_hand(*cards):
    h = Hand()
    for c in cards:
        h.add_card(c)
    h.calculate_total()
    return h


def test_ace_5():
    h = make_hand('A', 5)
    assert h.total == 16
    assert h.aces_counted_as_11 > 0
    assert h.total <= 21
    assert not (len(h.cards) == 2 and h.total == 21)


def test_ace_king():
    h = make_hand('A', 'K')
    assert h.total == 21
    assert h.aces_counted_as_11 > 0
    assert h.total <= 21
    assert len(h.cards) == 2 and h.total == 21


def test_ace_ace():
    h = make_hand('A', 'A')
    assert h.total == 12
    assert h.aces_counted_as_11 > 0
    assert h.total <= 21
    assert not (len(h.cards) == 2 and h.total == 21)


def test_ace_ace_9():
    h = make_hand('A', 'A', 9)
    assert h.total == 21
    assert h.aces_counted_as_11 > 0
    assert h.total <= 21
    assert not (len(h.cards) == 2 and h.total == 21)


def test_ace_ace_king():
    h = make_hand('A', 'A', 'K')
    assert h.total == 12
    assert h.aces_counted_as_11 == 0
    assert h.total <= 21
    assert not (len(h.cards) == 2 and h.total == 21)


def test_9_6():
    h = make_hand(9, 6)
    assert h.total == 15
    assert h.aces_counted_as_11 == 0
    assert h.total <= 21
    assert not (len(h.cards) == 2 and h.total == 21)


def test_king_queen():
    h = make_hand('K', 'Q')
    assert h.total == 20
    assert h.aces_counted_as_11 == 0
    assert h.total <= 21
    assert not (len(h.cards) == 2 and h.total == 21)


def test_7_8_9():
    h = make_hand(7, 8, 9)
    assert h.total == 24
    assert h.aces_counted_as_11 == 0
    assert h.total > 21
    assert not (len(h.cards) == 2 and h.total == 21)


def test_ace_9_5():
    h = make_hand('A', 9, 5)
    assert h.total == 15
    assert h.aces_counted_as_11 == 0
    assert h.total <= 21
    assert not (len(h.cards) == 2 and h.total == 21)


def test_5_5_ace():
    h = make_hand(5, 5, 'A')
    assert h.total == 21
    assert h.aces_counted_as_11 > 0
    assert h.total <= 21
    assert not (len(h.cards) == 2 and h.total == 21)

