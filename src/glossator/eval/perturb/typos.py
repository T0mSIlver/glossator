"""Keyboard slips, applied without a model."""

from __future__ import annotations

import random

MIN_TYPOS = 2
MAX_TYPOS = 4

# Physically adjacent keys on a QWERTY keyboard. A typo is a finger landing next
# door, so the substitutions come from the layout rather than from a letter
# confusion table, which is a different kind of mistake.
KEYBOARD_NEIGHBOURS: dict[str, str] = {
    "a": "qwsz",
    "b": "vghn",
    "c": "xdfv",
    "d": "serfcx",
    "e": "wsdr",
    "f": "drtgvc",
    "g": "ftyhbv",
    "h": "gyujnb",
    "i": "ujko",
    "j": "huikmn",
    "k": "jiolm",
    "l": "kop",
    "m": "njk",
    "n": "bhjm",
    "o": "iklp",
    "p": "ol",
    "q": "wa",
    "r": "edft",
    "s": "awedxz",
    "t": "rfgy",
    "u": "yhji",
    "v": "cfgb",
    "w": "qase",
    "x": "zsdc",
    "y": "tghu",
    "z": "asx",
}

TYPO_OPERATIONS = ("substitute", "transpose", "drop", "double")


def typo_variant(question: str, *, seed: int, question_id: str) -> str | None:
    """The question with two to four keyboard slips in it, or None if it is too short.

    Seeded by the run's seed and the question's id rather than by position, so the
    same question mistyped in two runs of the same seed comes out the same however
    the subset around it changed.
    """
    rng = random.Random(f"{seed}:{question_id}")
    positions = [
        index
        for index, character in enumerate(question)
        # The first letter of the question is left alone: a typo there reads as a
        # different word rather than as a slip, and search treats it as one.
        if index > 0 and character.lower() in KEYBOARD_NEIGHBOURS
    ]
    if len(positions) < MIN_TYPOS * 2:
        return None

    wanted = rng.randint(MIN_TYPOS, MAX_TYPOS)
    chosen: list[int] = []
    for index in rng.sample(positions, k=len(positions)):
        # Two slips in the same short word leave a token nothing can match, which
        # is a harder question than "the user mistyped"; spread them out.
        if all(abs(index - taken) > 2 for taken in chosen):
            chosen.append(index)
        if len(chosen) == wanted:
            break

    characters = list(question)
    for index in sorted(chosen, reverse=True):
        _apply_typo(characters, index, rng)
    variant = "".join(characters)
    return variant if variant != question else None


def _apply_typo(characters: list[str], index: int, rng: random.Random) -> None:
    character = characters[index]
    operation = rng.choice(TYPO_OPERATIONS)
    if operation == "transpose" and index + 1 < len(characters):
        characters[index], characters[index + 1] = characters[index + 1], character
        return
    if operation == "drop":
        del characters[index]
        return
    if operation == "double":
        characters.insert(index, character)
        return
    neighbours = KEYBOARD_NEIGHBOURS[character.lower()]
    replacement = rng.choice(neighbours)
    characters[index] = replacement.upper() if character.isupper() else replacement
