import argparse
import json
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))

from generate_intentional import generate_intentional
from generate_random import generate_random
from generate_reasoning import generate_reasoning, _get_hand_info

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def sanity_check(rows):
    total = len(rows)
    if total < 4000:
        raise ValueError(f"Too few rows: {total} (expected >= 4000)")

    hit_count = sum(1 for r in rows if r['action'] == 'hit')
    stand_count = total - hit_count
    hit_pct = hit_count / total * 100
    stand_pct = stand_count / total * 100

    if hit_pct > 75:
        raise ValueError(f"Hit% is {hit_pct:.1f}% — likely a generation bug (expected < 75%)")
    print(f"  Label distribution: hit={hit_pct:.1f}%  stand={stand_pct:.1f}%  OK")

    soft_rows = [r for r in rows if any(c == 'A' for c in r['cards'])]
    if not soft_rows:
        raise ValueError("No soft rows found — soft generation likely has a bug")
    print(f"  Soft rows present: {len(soft_rows)}  OK")

    hard_rows = [r for r in rows if not any(c == 'A' for c in r['cards'])]
    hard_cells = set()
    for r in hard_rows:
        total_val, _ = _get_hand_info(r['cards'])
        hard_cells.add((total_val, r['dealer_card']))
    if len(hard_cells) < 198:
        raise ValueError(f"Hard coverage {len(hard_cells)} unique cells — expected >= 198")
    print(f"  Hard coverage: {len(hard_cells)} unique cells  OK")

    soft_cells = set()
    for r in soft_rows:
        total_val, _ = _get_hand_info(r['cards'])
        soft_cells.add((total_val, r['dealer_card']))
    if len(soft_cells) < 110:
        raise ValueError(f"Soft coverage {len(soft_cells)} unique cells — expected >= 110")
    print(f"  Soft coverage: {len(soft_cells)} unique cells  OK")

    print(f"  Total rows: {total}  OK")


def deduplicate(rows):
    seen = set()
    result = []
    for row in rows:
        key = row['prompt']
        if key not in seen:
            seen.add(key)
            result.append(row)
    removed = len(rows) - len(result)
    if removed:
        print(f"Deduplication removed {removed} rows  ({len(result)} remain)")
    return result


def _has_case(rows, player_total, dealer_card, is_soft_hand):
    for row in rows:
        t, soft = _get_hand_info(row['cards'])
        if t == player_total and row['dealer_card'] == dealer_card and soft == is_soft_hand:
            return True
    return False


def stratified_split(rows, train_ratio=0.8, val_ratio=0.1):
    random.seed(42)

    hits = [r for r in rows if r['action'] == 'hit']
    stands = [r for r in rows if r['action'] == 'stand']
    random.shuffle(hits)
    random.shuffle(stands)

    def split_group(lst):
        n = len(lst)
        train_end = int(n * train_ratio)
        val_end = train_end + int(n * val_ratio)
        return lst[:train_end], lst[train_end:val_end], lst[val_end:]

    h_tr, h_va, h_te = split_group(hits)
    s_tr, s_va, s_te = split_group(stands)

    train = h_tr + s_tr
    val = h_va + s_va
    test = h_te + s_te

    random.shuffle(train)
    random.shuffle(val)
    random.shuffle(test)

    # Warn if edge cases are absent from any split
    for name, split in [("train", train), ("val", val), ("test", test)]:
        if not _has_case(split, 18, 'A', True):
            print(f"  WARNING: soft 18 vs Ace not in {name} split")
        if not _has_case(split, 16, 10, False):
            print(f"  WARNING: hard 16 vs 10 not in {name} split")

    return train, val, test


def write_jsonl(rows, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        for row in rows:
            f.write(json.dumps(row) + '\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true',
                        help='Skip API calls — fill reasoning with DRY_RUN placeholder')
    args = parser.parse_args()

    print("=== Stage 1: Generating rows ===")
    intentional_rows = generate_intentional()
    print(f"Intentional rows: {len(intentional_rows)}")

    random_rows = generate_random()
    print(f"Random rows: {len(random_rows)}")

    combined = intentional_rows + random_rows
    print(f"Combined: {len(combined)} rows\n")

    print("=== Sanity checks ===")
    sanity_check(combined)
    print()

    if args.dry_run:
        print("=== Dry run: skipping reasoning generation ===")
        rows = [{**r, 'reasoning': 'DRY_RUN'} for r in combined]
    else:
        print("=== Stage 2: Generating reasoning (Batch API) ===")
        rows = generate_reasoning(combined)
        print()

    print("=== Stage 3: Deduplicate, split, write ===")
    rows = deduplicate(rows)
    train, val, test = stratified_split(rows)

    train_path = os.path.join(DATA_DIR, "train.jsonl")
    val_path = os.path.join(DATA_DIR, "val.jsonl")
    test_path = os.path.join(DATA_DIR, "test.jsonl")

    write_jsonl(train, train_path)
    write_jsonl(val, val_path)
    write_jsonl(test, test_path)

    print(f"train={len(train)}  val={len(val)}  test={len(test)}")
    print(f"Written to: {os.path.abspath(DATA_DIR)}")


if __name__ == "__main__":
    main()
