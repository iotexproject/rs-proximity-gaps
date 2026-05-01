"""g3_count_pattern_analysis.py — analyze (DFT support → count) patterns.

From enum sweep at q=1153, parse all count > 0 supports and group by structural
features:
- (b-a, c-a, c-b) differences
- parity pattern (even/odd of each position)
- whether shifts by ±n_0/2, ±n_0/4 are present
"""
from collections import defaultdict, Counter

# All count > 0 supports from enum sweep at q=1153
count_data = {
    9: [(8,9,20),(8,9,21),(9,20,21),(10,11,22),(10,11,23),(11,22,23),
        (12,13,16),(12,13,17),(13,16,17),(14,15,18),(14,15,19),(15,18,19),
        (16,17,29),(16,28,29),(17,28,29),(18,19,31),(18,30,31),(19,30,31),
        (20,21,25),(20,24,25),(21,24,25),(22,23,27),(22,26,27),(23,26,27)],
    8: [(8,20,21),(10,22,23),(12,16,17),(14,18,19),(16,17,28),(18,19,30),
        (20,21,24),(22,23,26)],
    6: [(8,16,25),(8,17,25),(9,16,24),(9,17,24),(10,18,27),(10,19,26),
        (11,18,26),(11,19,26),(12,20,29),(12,21,29),(13,20,28),(13,21,28),
        (14,22,31),(14,23,31),(15,22,30),(15,23,30)],
    5: [(8,9,16),(8,9,17),(8,16,21),(9,16,17),(9,16,25),(10,11,18),(10,11,19),
        (10,18,23),(11,18,19),(11,18,27),(12,13,20),(12,13,21),(12,20,25),
        (13,20,21),(13,20,29),(14,15,22),(14,15,23),(14,22,27),(15,22,23),
        (15,22,31),(16,17,25),(16,24,25),(17,24,25),(18,19,27),(18,26,27),
        (19,26,27),(20,21,29),(20,28,29),(21,28,29)],
    4: [(8,9,24),(8,9,25),(8,16,17),(8,17,24),(8,24,25),(9,16,25),(9,24,25),
        (10,11,26),(10,11,27),(10,18,19),(10,19,26),(11,18,27),(11,26,27),
        (12,13,28),(12,13,29),(12,20,21),(12,21,28),(12,28,29),(13,28,29),
        (14,15,30),(14,15,31),(14,22,23),(14,23,30),(14,30,31),(15,22,31),
        (15,30,31),(16,17,24),(20,21,28),(22,23,30)],
}


def analyze_support(s):
    """Return (b-a, c-a, c-b, parity_pattern)."""
    a, b, c = sorted(s)
    return (b-a, c-a, c-b, ''.join('e' if x % 2 == 0 else 'o' for x in (a, b, c)))


def main():
    # For each count, group by (b-a, c-a, c-b) pattern
    for cnt in sorted(count_data, reverse=True):
        supports = count_data[cnt]
        diff_patterns = Counter()
        parity_patterns = Counter()
        for s in supports:
            d = analyze_support(s)
            diff_patterns[(d[0], d[1], d[2])] += 1
            parity_patterns[d[3]] += 1
        print(f"=== count = {cnt} ({len(supports)} supports) ===")
        print(f"  Diff patterns (b-a, c-a, c-b):")
        for k, v in sorted(diff_patterns.items()):
            print(f"    {k}: {v}")
        print(f"  Parity patterns:")
        for k, v in sorted(parity_patterns.items()):
            print(f"    {k}: {v}")
        print()


if __name__ == "__main__":
    main()
