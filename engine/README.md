# engine

Core blackjack game logic. Agents import from here but never modify it directly.

## Modules

### `deck.py` — `Deck`
A standard 52-card deck (2–10, J, Q, K, A × 4 suits). Cards are represented as integers for number cards and strings for face cards and aces. Auto-reshuffles when fewer than 15 cards remain.

| Method | Description |
|---|---|
| `shuffle()` | Randomly shuffles the deck in place |
| `draw()` | Pops and returns the top card, reshuffling first if low |

---

### `hand.py` — `Hand`
Tracks a single player or dealer hand. Call `add_card()` then `calculate_total()` after each draw — state is not updated automatically.

| Attribute | Type | Description |
|---|---|---|
| `cards` | `list` | All cards currently in the hand |
| `total` | `int` | Best valid total (≤ 21 when possible) |
| `aces_counted_as_11` | `int` | Number of aces still counted as 11 |
| `is_soft` | `bool` | True when at least one ace counts as 11 |
| `is_bust` | `bool` | True when total exceeds 21 |

| Method | Returns | Description |
|---|---|---|
| `add_card(card)` | — | Appends a card without recalculating |
| `calculate_total()` | — | Recomputes total and updates all flags |
| `check_natural_blackjack()` | `bool` | True when hand is exactly two cards totalling 21 |

---

### `gameState.py` — `GameState`
A plain data container passed from `Game` to agents. Agents read from this; they never write back to it.

| Attribute | Description |
|---|---|
| `player_hand` | The player's `Hand` instance |
| `player_total` | Numeric total of the player's hand |
| `is_soft` | Whether the player's hand is soft |
| `dealer_visible_card` | The dealer's face-up card |
| `available_actions` | `["hit", "stand"]` during play, `[]` when terminal |

---

### `game.py` — `Game`
Owns the full flow of a single hand. Coordinates `Deck`, `Hand`, and `GameState`. Only three methods are public.

| Method | Returns | Description |
|---|---|---|
| `reset()` | `GameState` | Deals opening cards, checks for natural blackjack, returns initial state |
| `step(action)` | `GameState` | Advances the game by one agent action (`"hit"` or `"stand"`) |
| `get_state()` | `GameState` | Packages current internal state; safe to call at any point |

**Reward structure:** win → `+1`, loss → `-1`, draw → `0`.

Natural blackjack is resolved immediately after the deal. On stand, the dealer hits until total ≥ 17.

---

### `text_serializer.py` — `serialize_state`
Converts a `GameState` into a human-readable string for CLI or logging use.

```
Your hand: A, K (total: 21, soft)
Dealer showing: 7
What do you do? Hit or Stand?
```

## Data flow

```
Deck  →  Game  →  GameState  →  Agent
          ↑                        |
          └────── action ("hit" / "stand") ──┘
```
