import random
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine.game import Game
from engine.text_serializer import serialize_state
from agents.basic_strategy_agent import BasicStrategyAgent


def generate_random(n_games: int = 2500) -> list[dict]:
    game = Game()
    agent = BasicStrategyAgent()
    rows = []

    for _ in range(n_games):
        state = game.reset()

        if game.is_terminal:
            continue

        while not game.is_terminal:
            template = random.choice(['A', 'B', 'C'])
            prompt = serialize_state(state, template)
            action = agent.act(state)

            rows.append({
                "prompt": prompt,
                "action": action,
                "template_id": template,
                "source": "random",
                "cards": list(state.player_hand.cards),
                "dealer_card": state.dealer_visible_card,
            })

            state = game.step(action)

    return rows


if __name__ == "__main__":
    rows = generate_random()
    print(f"Total rows: {len(rows)}")