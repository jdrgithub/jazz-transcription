"""
Serialize detector analysis results into a compact payload for OpenAI.
"""

from typing import Any, Dict, List, Optional


def _round(value: Optional[float], digits: int = 3) -> Optional[float]:
    if value is None:
        return None
    try:
        return round(float(value), digits)
    except (TypeError, ValueError):
        return None


def _serialize_scale_patterns(scale_analysis: Any, limit: int = 25) -> List[Dict[str, Any]]:
    patterns = getattr(scale_analysis, "detected_scales", None) or []
    serialized = []
    for pattern in patterns[:limit]:
        serialized.append({
            "name": getattr(pattern, "name", "Unknown"),
            "root": getattr(pattern, "root", None),
            "confidence": _round(getattr(pattern, "confidence", None), 2),
            "start_time": _round(getattr(pattern, "start_time", None)),
            "end_time": _round(getattr(pattern, "end_time", None)),
        })
    return serialized


def _serialize_arpeggio_patterns(arpeggio_analysis: Any, limit: int = 25) -> List[Dict[str, Any]]:
    patterns = getattr(arpeggio_analysis, "detected_arpeggios", None) or []
    serialized = []
    for pattern in patterns[:limit]:
        serialized.append({
            "name": getattr(pattern, "name", "Unknown"),
            "root": getattr(pattern, "root", None),
            "chord_type": getattr(pattern, "chord_type", None),
            "direction": getattr(pattern, "direction", None),
            "confidence": _round(getattr(pattern, "confidence", None), 2),
            "octave_span": getattr(pattern, "octave_span", None),
            "start_time": _round(getattr(pattern, "start_time", None)),
            "end_time": _round(getattr(pattern, "end_time", None)),
        })
    return serialized


def _serialize_approach_patterns(approach_analysis: Any, limit: int = 25) -> List[Dict[str, Any]]:
    patterns = getattr(approach_analysis, "detected_patterns", None) or []
    serialized = []
    for pattern in patterns[:limit]:
        serialized.append({
            "name": getattr(pattern, "name", "Unknown"),
            "pattern_type": getattr(pattern, "pattern_type", None),
            "direction": getattr(pattern, "direction", None),
            "confidence": _round(getattr(pattern, "confidence", None), 2),
            "resolution_strength": _round(getattr(pattern, "resolution_strength", None), 2),
            "start_time": _round(getattr(pattern, "start_time", None)),
            "end_time": _round(getattr(pattern, "end_time", None)),
        })
    return serialized


def build_analysis_payload(
    scale_analysis: Any,
    arpeggio_analysis: Any,
    approach_analysis: Any,
    solo_metadata: Dict[str, Any],
    chord_changes: Optional[str] = None,
    max_patterns: int = 25,
) -> Dict[str, Any]:
    """
    Build a compact JSON-serializable payload from detector outputs.

    Raw note lists are omitted; only summarized pattern findings are included.
    """
    most_common_scales = getattr(scale_analysis, "most_common_scales", None) or []
    most_common_arpeggios = getattr(arpeggio_analysis, "most_common_arpeggios", None) or []
    most_common_approaches = getattr(approach_analysis, "most_common_patterns", None) or []
    chord_progression = getattr(arpeggio_analysis, "chord_progression", None) or []

    # Truncate long chord-change strings
    chord_text = chord_changes or solo_metadata.get("chord_changes") or ""
    if isinstance(chord_text, str) and len(chord_text) > 2000:
        chord_text = chord_text[:2000] + "…"

    return {
        "metadata": {
            "title": solo_metadata.get("title", "Unknown Solo"),
            "performer": solo_metadata.get("performer", "Unknown Performer"),
            "key": solo_metadata.get("key", "Unknown Key"),
            "tempo": solo_metadata.get("tempo"),
            "instrument": solo_metadata.get("instrument"),
            "style": solo_metadata.get("style"),
            "total_notes": solo_metadata.get("total_notes", 0),
            "chord_changes": chord_text or None,
        },
        "scales": {
            "key_signature": getattr(scale_analysis, "key_signature", None),
            "coverage_percent": _round(getattr(scale_analysis, "scale_coverage", 0.0), 1),
            "most_common": [
                {"name": name, "count": count}
                for name, count in most_common_scales[:10]
            ],
            "top_patterns": _serialize_scale_patterns(scale_analysis, max_patterns),
            "total_detected": len(getattr(scale_analysis, "detected_scales", None) or []),
        },
        "arpeggios": {
            "coverage_percent": _round(getattr(arpeggio_analysis, "arpeggio_coverage", 0.0), 1),
            "most_common": [
                {"name": name, "count": count}
                for name, count in most_common_arpeggios[:10]
            ],
            "top_patterns": _serialize_arpeggio_patterns(arpeggio_analysis, max_patterns),
            "total_detected": len(getattr(arpeggio_analysis, "detected_arpeggios", None) or []),
            "chord_progression_sample": [
                {"chord": chord, "time": _round(time)}
                for chord, time in chord_progression[:40]
            ],
        },
        "approach_tones": {
            "coverage_percent": _round(getattr(approach_analysis, "approach_coverage", 0.0), 1),
            "most_common": [
                {"name": name, "count": count}
                for name, count in most_common_approaches[:10]
            ],
            "top_patterns": _serialize_approach_patterns(approach_analysis, max_patterns),
            "total_detected": len(getattr(approach_analysis, "detected_patterns", None) or []),
        },
    }
