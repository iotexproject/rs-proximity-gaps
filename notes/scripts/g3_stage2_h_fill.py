"""g3_stage2_h_fill.py — fill in h=11,13,14,15 and try h=20."""
import sys

sys.path.insert(0, "notes/scripts")
from g3_stage2_h7_grevlex import test_h_grevlex


def main():
    for h in [11, 13, 14, 15]:
        test_h_grevlex(h, 17, 3, 16)


if __name__ == "__main__":
    main()
