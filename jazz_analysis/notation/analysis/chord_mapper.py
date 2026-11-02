"""
Map Weimar melody notes onto beat-level chords and produce chord-specific advice.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from notation.analysis.pitch_utils import pitch_class_name


# Interval sets relative to chord root (pitch classes).
SCALE_OPTIONS: Dict[str, List[Tuple[str, List[int]]]] = {
    "major": [
        ("Ionian (major)", [0, 2, 4, 5, 7, 9, 11]),
        ("Lydian", [0, 2, 4, 6, 7, 9, 11]),
        ("Major pentatonic", [0, 2, 4, 7, 9]),
    ],
    "major6": [
        ("Ionian (major)", [0, 2, 4, 5, 7, 9, 11]),
        ("Major pentatonic", [0, 2, 4, 7, 9]),
    ],
    "dominant": [
        ("Mixolydian", [0, 2, 4, 5, 7, 9, 10]),
        ("Lydian dominant", [0, 2, 4, 6, 7, 9, 10]),
        ("Blues scale", [0, 3, 5, 6, 7, 10]),
        ("Half-whole diminished", [0, 1, 3, 4, 6, 7, 9, 10]),
        ("Altered (super Locrian)", [0, 1, 3, 4, 6, 8, 10]),
    ],
    "minor7": [
        ("Dorian", [0, 2, 3, 5, 7, 9, 10]),
        ("Aeolian (natural minor)", [0, 2, 3, 5, 7, 8, 10]),
        ("Minor pentatonic", [0, 3, 5, 7, 10]),
        ("Blues scale", [0, 3, 5, 6, 7, 10]),
    ],
    "half_dim": [
        ("Locrian", [0, 1, 3, 5, 6, 8, 10]),
        ("Locrian #2", [0, 2, 3, 5, 6, 8, 10]),
    ],
    "diminished": [
        ("Whole-half diminished", [0, 2, 3, 5, 6, 8, 9, 11]),
    ],
    "augmented": [
        ("Whole tone", [0, 2, 4, 6, 8, 10]),
    ],
    "sus": [
        ("Mixolydian", [0, 2, 4, 5, 7, 9, 10]),
        ("Suspended pentatonic", [0, 2, 5, 7, 10]),
    ],
}

ARPEGGIO_TONES: Dict[str, List[int]] = {
    "major": [0, 4, 7, 11],
    "major6": [0, 4, 7, 9],
    "dominant": [0, 4, 7, 10],
    "minor7": [0, 3, 7, 10],
    "half_dim": [0, 3, 6, 10],
    "diminished": [0, 3, 6, 9],
    "augmented": [0, 4, 8],
    "sus": [0, 5, 7, 10],
}


@dataclass
class ChordSpan:
    chord: str
    quality: str
    root_pc: int
    start_onset: float
    end_onset: float
    bar: Optional[int]
    beat: Optional[int]
    form: str = ""
    notes: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ChordAdvice:
    chord: str
    quality: str
    bar: Optional[int]
    beat: Optional[int]
    form: str
    start_onset: float
    end_onset: float
    note_count: int
    pitch_classes_played: List[str]
    best_scale: Optional[str]
    scale_fit: float
    alternate_scales: List[str]
    chord_tones_hit: List[str]
    missing_chord_tones: List[str]
    actionable: str


def parse_chord_symbol(symbol: str) -> Tuple[Optional[int], str]:
    """Return (root_pitch_class, quality_key) for a Weimar-style chord symbol."""
    if not symbol or not symbol.strip():
        return None, "unknown"

    s = symbol.strip()
    if s[0] not in "ABCDEFG":
        return None, "unknown"

    if len(s) > 1 and s[1] in "#b":
        root_token = s[:2]
        rest = s[2:]
    else:
        root_token = s[0]
        rest = s[1:]

    root_map = {
        "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "Fb": 4,
        "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10,
        "Bb": 10, "B": 11, "Cb": 11,
    }
    root_pc = root_map.get(root_token)
    if root_pc is None:
        return None, "unknown"

    rest = rest.strip()
    rest_l = rest.lower()

    if rest.startswith("-") or rest_l.startswith("m") or rest_l.startswith("min"):
        if "b5" in rest_l or "ø" in rest:
            return root_pc, "half_dim"
        return root_pc, "minor7"
    if "dim" in rest_l or rest.startswith("o") or "°" in rest:
        return root_pc, "diminished"
    if "aug" in rest_l or rest.startswith("+"):
        return root_pc, "augmented"
    if "sus" in rest_l:
        return root_pc, "sus"
    if "maj7" in rest_l or "ma7" in rest_l or "j7" in rest_l or "Δ" in rest:
        return root_pc, "major"
    if rest.startswith("6") or rest == "6":
        return root_pc, "major6"
    if rest.startswith("7") or "9" in rest or "13" in rest or "alt" in rest_l:
        return root_pc, "dominant"
    if "7" in rest:
        return root_pc, "dominant"
    if rest == "" or rest_l in {"maj", "ma"}:
        return root_pc, "major"
    return root_pc, "major"


def load_chord_timeline(db_path: str, melid: int) -> List[Tuple[float, float, str, Optional[int], Optional[int], str]]:
    """
    Build forward-filled chord spans from Weimar beats table.

    Returns list of (start_onset, end_onset, chord, bar, beat, form).
    """
    import sqlite3

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT onset, bar, beat, chord, form
        FROM beats
        WHERE melid = ?
        ORDER BY onset
        """,
        (melid,),
    )
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return []

    filled = []
    current_chord = ""
    for onset, bar, beat, chord, form in rows:
        if chord and chord.strip():
            current_chord = chord.strip()
        filled.append({
            "onset": float(onset),
            "bar": bar,
            "beat": beat,
            "chord": current_chord,
            "form": form or "",
        })

    spans = []
    i = 0
    while i < len(filled):
        start = filled[i]
        if not start["chord"]:
            i += 1
            continue
        j = i + 1
        while j < len(filled) and filled[j]["chord"] == start["chord"]:
            j += 1
        end_onset = filled[j]["onset"] if j < len(filled) else start["onset"] + 2.0
        spans.append((
            start["onset"],
            end_onset,
            start["chord"],
            start["bar"],
            start["beat"],
            start["form"],
        ))
        i = j
    return spans


def assign_notes_to_chords(notes: List[Dict[str, Any]], spans: List[Tuple]) -> List[ChordSpan]:
    """Attach notes to chord spans by onset."""
    chord_spans: List[ChordSpan] = []
    for start, end, chord, bar, beat, form in spans:
        root_pc, quality = parse_chord_symbol(chord)
        if root_pc is None:
            quality = "unknown"
            root_pc = 0
        chord_spans.append(ChordSpan(
            chord=chord,
            quality=quality,
            root_pc=root_pc,
            start_onset=start,
            end_onset=end,
            bar=bar,
            beat=beat,
            form=form,
        ))

    for note in notes:
        onset = float(note["onset"])
        for span in chord_spans:
            if span.start_onset <= onset < span.end_onset:
                span.notes.append(note)
                break
    return chord_spans


def _fit_scale(pitch_classes: List[int], root_pc: int, intervals: List[int]) -> float:
    if not pitch_classes:
        return 0.0
    scale = {(root_pc + i) % 12 for i in intervals}
    hits = sum(1 for pc in pitch_classes if pc in scale)
    return hits / len(pitch_classes)


def advise_chord_span(span: ChordSpan) -> Optional[ChordAdvice]:
    if not span.notes:
        return None

    pcs = [int(round(n["pitch"])) % 12 for n in span.notes]
    pc_names = sorted({pitch_class_name(pc) for pc in pcs})

    options = SCALE_OPTIONS.get(span.quality, SCALE_OPTIONS["major"])
    scored = []
    for name, intervals in options:
        scored.append((name, _fit_scale(pcs, span.root_pc, intervals), intervals))
    scored.sort(key=lambda x: x[1], reverse=True)

    best_name, best_fit, best_intervals = scored[0]
    alternates = [name for name, fit, _ in scored[1:3] if fit >= 0.5]

    arp = ARPEGGIO_TONES.get(span.quality, ARPEGGIO_TONES["major"])
    arp_pcs = {(span.root_pc + i) % 12 for i in arp}
    hit = sorted(arp_pcs.intersection(pcs))
    missing = sorted(arp_pcs - set(pcs))
    hit_names = [pitch_class_name(pc) for pc in hit]
    missing_names = [pitch_class_name(pc) for pc in missing]

    # Build concrete actionable line
    root_name = pitch_class_name(span.root_pc)
    arp_desc = "/".join(pitch_class_name((span.root_pc + i) % 12) for i in arp[:4])
    location = ""
    if span.form:
        location = f" ({span.form})"
    elif span.bar is not None:
        location = f" (bar {span.bar})"

    actionable = (
        f"Over {span.chord}{location}: play {root_name} {best_name} "
        f"(~{best_fit*100:.0f}% fit with what was played); "
        f"outline the {span.chord} sound with {arp_desc}"
    )
    if missing_names:
        actionable += f"; chord tones not emphasized here: {', '.join(missing_names)}"
    if alternates:
        actionable += f"; also works: {', '.join(alternates)}"

    return ChordAdvice(
        chord=span.chord,
        quality=span.quality,
        bar=span.bar,
        beat=span.beat,
        form=span.form,
        start_onset=span.start_onset,
        end_onset=span.end_onset,
        note_count=len(span.notes),
        pitch_classes_played=pc_names,
        best_scale=best_name,
        scale_fit=round(best_fit, 3),
        alternate_scales=alternates,
        chord_tones_hit=hit_names,
        missing_chord_tones=missing_names,
        actionable=actionable,
    )


def build_chord_advice_report(db_path: str, melid: int, notes: List[Dict[str, Any]]) -> List[ChordAdvice]:
    """Full pipeline: beats → spans → per-chord actionable advice."""
    spans = load_chord_timeline(db_path, int(melid))
    chord_spans = assign_notes_to_chords(notes, spans)
    advice = []
    for span in chord_spans:
        item = advise_chord_span(span)
        if item and item.note_count > 0:
            advice.append(item)
    return advice


def advice_to_payload(advice_list: List[ChordAdvice], limit: int = 80) -> List[Dict[str, Any]]:
    """Serialize for OpenAI / export."""
    payload = []
    for item in advice_list[:limit]:
        payload.append({
            "chord": item.chord,
            "bar": item.bar,
            "beat": item.beat,
            "form": item.form,
            "note_count": item.note_count,
            "pitches_played": item.pitch_classes_played,
            "best_scale": item.best_scale,
            "scale_fit": item.scale_fit,
            "alternate_scales": item.alternate_scales,
            "chord_tones_hit": item.chord_tones_hit,
            "missing_chord_tones": item.missing_chord_tones,
            "play_this": item.actionable,
        })
    return payload
