import random
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine.hand import Hand
from engine.gameState import GameState
from agents.basic_strategy_agent import BasicStrategyAgent
from engine.text_serializer import serialize_state


def get_hard_combos(total: int) -> list[list]:
    result = []
    seen = set()
    for low in range(2, 10+1):
        high = total - low
        if 2 <= high <= 10:
            key = tuple(sorted([low, high]))
            if key not in seen:
                seen.add(key)
                result.append([low, high])
    for a in range(2, 7+1):
        for b in range(a, 7+1):
            c = total - a - b
            if 2 <= c <= 10:
                key = tuple(sorted([a, b, c]))
                if key not in seen:
                    seen.add(key)
                    result.append([a, b, c])
    return result[:4]

def get_soft_combos(total: int) -> list[list]:
    other = total - 11
    if other == 1:
        return [['A', 'A']]
    elif 2 <= other <= 10:
        return [['A', other]]
    else:
        return []


def make_row(cards: list, dealer_card, template_id: str) -> dict:
    hand = Hand()
    for card in cards:
        hand.add_card(card)
    hand.calculate_total()

    state = GameState(hand, hand.total, hand.is_soft, dealer_card, ["hit", "stand"])
    action = BasicStrategyAgent().act(state)
    prompt = serialize_state(state, template_id)
    return {"prompt": prompt,
            "action": action,
            "template_id": template_id,
            "source": "intentional",
            "cards": cards,
            "dealer_card": dealer_card}


def generate_intentional() -> list[dict]:
    dealer_cards = [2, 3, 4, 5, 6, 7, 8, 9, 10, 'A']
    rows = []
    for total in range(4, 21+1):
        for d_card in dealer_cards:
            for cards in get_hard_combos(total):
                template = random.choice(['A', 'B', 'C'])
                rows.append(make_row(cards, d_card, template))
    for total in range(12, 21+1):
        for d_card in dealer_cards:
            for cards in get_soft_combos(total):
                template = random.choice(['A', 'B', 'C'])
                rows.append(make_row(cards, d_card, template))
    hard_rows = [r for r in rows if not any(c == 'A' for c in r['cards'])]
    soft_rows = [r for r in rows if any(c == 'A' for c in r['cards'])]
    print(f"Hard rows: {len(hard_rows)}, Soft rows: {len(soft_rows)}")
    return rows


if __name__ == "__main__":
    rows = generate_intentional()
    print(f"Total rows: {len(rows)}")
