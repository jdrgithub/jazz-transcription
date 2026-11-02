"""
Lightweight pitch helpers so detectors can run without music21.
"""

from typing import Optional

NOTE_NAMES = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]


def pitch_class_name(pitch_value: int) -> str:
    """Return a note name for a MIDI pitch or pitch class (0-11)."""
    return NOTE_NAMES[int(pitch_value) % 12]


def estimate_key_signature(pitches: list) -> Optional[str]:
    """
    Rough major/minor key estimate from pitch-class histogram.

    Used when music21 is unavailable. Prefer music21's key analysis when present.
    """
    if not pitches:
        return None

    counts = [0] * 12
    for p in pitches:
        counts[int(p) % 12] += 1

    # Krumhansl-Schmuckler-ish major/minor profiles (simplified)
    major_profile = [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
    minor_profile = [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]

    best_score = float("-inf")
    best_key = None
    for root in range(12):
        rotated = counts[root:] + counts[:root]
        major_score = sum(a * b for a, b in zip(rotated, major_profile))
        minor_score = sum(a * b for a, b in zip(rotated, minor_profile))
        if major_score > best_score:
            best_score = major_score
            best_key = f"{NOTE_NAMES[root]} major"
        if minor_score > best_score:
            best_score = minor_score
            best_key = f"{NOTE_NAMES[root]} minor"
    return best_key
