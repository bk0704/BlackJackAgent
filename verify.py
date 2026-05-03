from engine.game import Game
from agents.basic_strategy_agent import BasicStrategyAgent


def main():
    game = Game()
    agent = BasicStrategyAgent()

    n = 10000
    wins = losses = draws = 0

    for _ in range(n):
        state = game.reset()
        while not game.is_terminal:
            action = agent.act(state)
            state = game.step(action)

        if game.reward == 1.0:
            wins += 1
        elif game.reward == -1.0:
            losses += 1
        else:
            draws += 1

    win_rate = wins / n
    loss_rate = losses / n
    draw_rate = draws / n

    print(f"Results over {n} hands:")
    print(f"  Wins:   {win_rate * 100:.1f}% ({wins})")
    print(f"  Losses: {loss_rate * 100:.1f}% ({losses})")
    print(f"  Draws:  {draw_rate * 100:.1f}% ({draws})")
    print()

    if 0.42 <= win_rate <= 0.45:
        print(f"PASS: Win rate {win_rate * 100:.1f}% is within expected range (42-45%)")
    else:
        print(f"FAIL: Win rate {win_rate * 100:.1f}% is OUTSIDE expected range (42-45%) — check engine for bugs")


if __name__ == "__main__":
    main()
