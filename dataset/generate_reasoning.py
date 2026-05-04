import os
import sys
import json
import time
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine.hand import Hand

MODEL = "claude-haiku-4-5-20251001"
MAX_TOKENS = 250
CHECKPOINT_PATH = os.path.join(os.path.dirname(__file__), "batch_checkpoint.json")


def _get_hand_info(cards):
    hand = Hand()
    for card in cards:
        hand.add_card(card)
    hand.calculate_total()
    return hand.total, hand.is_soft


def build_reasoning_prompt(row):
    total, is_soft = _get_hand_info(row['cards'])
    hand_type = "soft" if is_soft else "hard"
    dealer = row['dealer_card']
    action = row['action'].capitalize()
    cards_str = ", ".join(str(c) for c in row['cards'])

    return (
        f"In blackjack, a player holds {cards_str} — a {hand_type} total of {total}. "
        f"The dealer is showing a {dealer}.\n\n"
        f"The correct play is: {action}.\n\n"
        f"Explain in 3–5 sentences why {action.lower()} is the correct decision. "
        f"Reference the dealer's likely total range given their upcard, the player's bust risk if hitting, "
        f"and the expected outcome of standing. Do not simply state that basic strategy says so — "
        f"explain the underlying logic. "
        f'End your response with the action on its own line: either "Hit." or "Stand."'
    )


def is_valid_reasoning(reasoning, action, dealer_card=None):
    sentences = [s.strip() for s in re.split(r'[.!?]+', reasoning) if s.strip()]
    if len(sentences) < 2:
        return False

    _face_patterns = {
        'J': r'\b([Jj]|[Jj]ack)\b',
        'Q': r'\b([Qq]|[Qq]ueen)\b',
        'K': r'\b([Kk]|[Kk]ing)\b',
    }

    if dealer_card is not None:
        if dealer_card == 'A':
            if not re.search(r'\b[Aa]ce\b', reasoning):
                return False
        elif dealer_card in _face_patterns:
            if not re.search(_face_patterns[dealer_card], reasoning):
                return False
        else:
            if not re.search(rf'\b{dealer_card}\b', reasoning):
                return False
    else:
        generic = r'\b([2-9]|10|[Aa]ce|[Jj]ack|[Qq]ueen|[Kk]ing|[JjQqKk])\b'
        if not re.search(generic, reasoning):
            return False

    if 'basic strategy' in reasoning.lower():
        analytical = {'bust', 'dealer', 'total', 'risk', 'range', 'likely', 'probability'}
        if not any(w in reasoning.lower() for w in analytical):
            return False

    m = re.search(r'\b(hit|stand)\s*\.\s*$', reasoning.strip(), re.IGNORECASE)
    if not m:
        return False
    if m.group(1).lower() != action.lower():
        return False

    return True


def generate_reasoning(rows):
    from dotenv import load_dotenv
    import anthropic
    load_dotenv()
    client = anthropic.Anthropic()

    enriched = []
    for row in rows:
        total, is_soft = _get_hand_info(row['cards'])
        enriched.append({**row, '_total': total, '_is_soft': is_soft})

    groups = {}
    for row in enriched:
        key = (row['_total'], str(row['dealer_card']), row['action'])
        if key not in groups:
            groups[key] = []
        groups[key].append(row)

    print(f"Unique strategy cells: {len(groups)}  (from {len(rows)} total rows)")

    batch_id = None
    if os.path.exists(CHECKPOINT_PATH):
        with open(CHECKPOINT_PATH) as f:
            checkpoint = json.load(f)
        batch_id = checkpoint.get('batch_id')
        print(f"Resuming batch {batch_id} from checkpoint")

    if batch_id is None:
        requests = []
        for key, group in groups.items():
            total, dealer_str, action = key
            prompt = build_reasoning_prompt(group[0])
            requests.append({
                "custom_id": f"{total}_{dealer_str}_{action}",
                "params": {
                    "model": MODEL,
                    "max_tokens": MAX_TOKENS,
                    "messages": [{"role": "user", "content": prompt}]
                }
            })

        batch = client.messages.batches.create(requests=requests)
        batch_id = batch.id
        with open(CHECKPOINT_PATH, 'w') as f:
            json.dump({"batch_id": batch_id}, f)
        print(f"Batch submitted: {batch_id}  ({len(requests)} requests)")

    while True:
        batch = client.messages.batches.retrieve(batch_id)
        c = batch.request_counts
        print(f"  {batch.processing_status} — succeeded={c.succeeded} errored={c.errored} processing={c.processing}")
        if batch.processing_status == "ended":
            break
        time.sleep(60)

    key_to_reasoning = {}
    discard_count = 0

    for result in client.messages.batches.results(batch_id):
        cid = result.custom_id
        parts = cid.split('_')
        total_val, dealer_str, action = int(parts[0]), parts[1], parts[2]
        key = (total_val, dealer_str, action)

        if result.result.type != "succeeded":
            print(f"  API error for {cid}")
            discard_count += 1
            continue

        reasoning = result.result.message.content[0].text
        rep_row = groups[key][0]

        if is_valid_reasoning(reasoning, action, rep_row['dealer_card']):
            key_to_reasoning[key] = reasoning
        else:
            print(f"  Validation failed for {cid}, retrying...")
            retry = client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                messages=[{"role": "user", "content": build_reasoning_prompt(rep_row)}]
            )
            retry_reasoning = retry.content[0].text
            if is_valid_reasoning(retry_reasoning, action, rep_row['dealer_card']):
                key_to_reasoning[key] = retry_reasoning
            else:
                print(f"  Discarding {cid} after retry")
                discard_count += 1

    if os.path.exists(CHECKPOINT_PATH):
        os.remove(CHECKPOINT_PATH)

    result_rows = []
    for key, group in groups.items():
        if key not in key_to_reasoning:
            continue
        reasoning = key_to_reasoning[key]
        for row in group:
            clean = {k: v for k, v in row.items() if not k.startswith('_')}
            clean['reasoning'] = reasoning
            result_rows.append(clean)

    total_groups = len(groups)
    print(f"Discarded {discard_count}/{total_groups} cells ({discard_count / total_groups * 100:.1f}%)")
    print(f"Rows with reasoning: {len(result_rows)}")
    return result_rows
