#!/usr/bin/env python3
"""Render the narrative cards used by the README recording.

These are the only frames that are not produced by a DocCanon command. They
frame the walkthrough; every status, diff, and finding shown between them is
emitted by the real helper.

Usage:
    python3 demo/card.py title
    python3 demo/card.py caption "text"
    python3 demo/card.py closing
"""

from __future__ import annotations

import sys

DIM = "\033[2m"
BOLD = "\033[1m"
CYAN = "\033[36m"
RESET = "\033[0m"


def title() -> None:
    print("\n" * 6)
    print(f"   {BOLD}DocCanon{RESET}")
    print()
    print("   Stop making every coding agent")
    print("   rediscover your codebase.")
    print()
    print(f"{DIM}   Governed, verifiable project context beside the code.{RESET}")
    print()


def caption(text: str) -> None:
    print()
    print(f"   {BOLD}{CYAN}>{RESET}{BOLD}{CYAN} {text}{RESET}")
    print()


def closing() -> None:
    print("\n" * 6)
    print("   Read the map first.")
    print("   Verify against the territory.")
    print()
    print(f"{DIM}   Reuse context.  Keep it fresh.  Switch agents.{RESET}")
    print()
    print(f"{DIM}   github.com/Heluhan/Doccanon{RESET}")
    print()


def main(argv: list[str]) -> int:
    if not argv:
        raise SystemExit(__doc__)
    command, *rest = argv
    if command == "title":
        title()
    elif command == "caption":
        caption(" ".join(rest))
    elif command == "closing":
        closing()
    else:
        raise SystemExit(f"unknown card: {command}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
