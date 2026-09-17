"""Owned process; survives browser disconnect, never restarts uncertain requests."""

import sys

from .lib import Unfold

if __name__ == "__main__":
    Unfold(sys.argv[1], sys.argv[2]).run_review_job(sys.argv[3])
