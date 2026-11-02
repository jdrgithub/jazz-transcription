"""
OpenAI client for turning structured solo analysis into plain-English insights.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, List, Optional

from notation.analysis.analysis_payload import build_analysis_payload
from notation.analysis.summary_generator import AnalysisSummary, JazzAnalysisSummaryGenerator

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an experienced jazz educator writing high-level solo analysis for practicing musicians.

You receive structured findings from algorithmic detectors (scales, arpeggios, approach tones). Treat those findings as the only musical facts you may use. Do not invent patterns, scales, arpeggios, or approach tones that are not supported by the data. If coverage or confidence is weak, say so plainly.

Write in plain English. Focus on musical character and practice value. Avoid histograms, raw MIDI dumps, and dense technical jargon.

Respond with a single JSON object only (no markdown fences) using exactly these keys:
{
  "overall_character": "string",
  "technical_level": "string",
  "harmonic_sophistication": "string",
  "scale_insights": ["string", ...],
  "arpeggio_insights": ["string", ...],
  "approach_insights": ["string", ...],
  "melodic_characteristics": ["string", ...],
  "recommendations": ["string", ...]
}

Use 2-5 short bullet strings for each list field.
"""

CHORD_PRACTICE_PROMPT = """You are a jazz improvisation coach. You receive per-chord analysis of a transcribed solo.

Your job is to turn each chord event into a SPECIFIC practice instruction in this exact style:
"Over <chord> (bar/form): play <scale or device>. Outline <chord tones>. Practice lick idea: <short concrete idea>."

Rules:
- Use ONLY the provided chord/scale/tone facts. Do not invent chords that are not listed.
- Prefer the best_scale and play_this fields already computed.
- Be concrete and actionable. No vague character talk.
- Group repeated identical chords briefly if needed, but keep bar/form references.
- Skip empty / no-note chords.

Respond with a single JSON object only:
{
  "headline": "one sentence describing the harmonic game of this solo",
  "practice_lines": ["Over ...", "Over ...", ...],
  "priority_drills": ["2-4 short drills that cover the hardest or most common moves"]
}
"""


class OpenAIAnalysisError(Exception):
    """Raised when OpenAI analysis cannot be completed."""


class OpenAIJazzAnalyzer:
    """Generate AnalysisSummary prose from detector outputs via OpenAI."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",
        fallback_generator: Optional[JazzAnalysisSummaryGenerator] = None,
    ):
        # None means "read from environment"; empty string means explicitly unset.
        if api_key is None:
            self.api_key = os.environ.get("OPENAI_API_KEY")
        else:
            self.api_key = api_key
        self.model = os.environ.get("OPENAI_MODEL", model)
        self.fallback_generator = fallback_generator or JazzAnalysisSummaryGenerator()
        self._client = None

    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key.strip())

    def _get_client(self):
        if self._client is not None:
            return self._client
        if not self.api_key:
            raise OpenAIAnalysisError(
                "OPENAI_API_KEY is not set. Export it before using AI analysis."
            )
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise OpenAIAnalysisError(
                "openai package is not installed. Run: pip install openai"
            ) from exc
        self._client = OpenAI(api_key=self.api_key)
        return self._client

    def generate_chord_practice_guide(
        self,
        solo_metadata: Dict[str, Any],
        chord_advice_payload: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Ask OpenAI to polish chord-mapped practice lines."""
        client = self._get_client()
        user_content = json.dumps(
            {
                "solo": solo_metadata,
                "chord_events": chord_advice_payload,
            },
            indent=2,
        )
        response = client.chat.completions.create(
            model=self.model,
            temperature=0.3,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": CHORD_PRACTICE_PROMPT},
                {
                    "role": "user",
                    "content": (
                        "Write specific over-this-chord practice instructions "
                        "from this analysis:\n\n" + user_content
                    ),
                },
            ],
        )
        content = response.choices[0].message.content
        if not content:
            raise OpenAIAnalysisError("Empty response from OpenAI")
        data = json.loads(content)
        if not isinstance(data, dict):
            raise OpenAIAnalysisError("OpenAI response was not a JSON object")
        return data

    def generate_summary(
        self,
        scale_analysis: Any,
        arpeggio_analysis: Any,
        approach_analysis: Any,
        solo_metadata: Dict[str, Any],
        chord_changes: Optional[str] = None,
        use_fallback_on_error: bool = True,
    ) -> AnalysisSummary:
        """
        Build detector payload, ask OpenAI for prose insights, return AnalysisSummary.

        On failure, optionally falls back to the rule-based summary generator.
        """
        coverage = {
            "scales": getattr(scale_analysis, "scale_coverage", 0.0) or 0.0,
            "arpeggios": getattr(arpeggio_analysis, "arpeggio_coverage", 0.0) or 0.0,
            "approach_tones": getattr(approach_analysis, "approach_coverage", 0.0) or 0.0,
        }

        try:
            payload = build_analysis_payload(
                scale_analysis,
                arpeggio_analysis,
                approach_analysis,
                solo_metadata,
                chord_changes=chord_changes,
            )
            insights = self._request_insights(payload)
            return AnalysisSummary(
                solo_title=solo_metadata.get("title", "Unknown Solo"),
                performer=solo_metadata.get("performer", "Unknown Performer"),
                key_signature=solo_metadata.get("key", "Unknown Key"),
                tempo=solo_metadata.get("tempo"),
                total_notes=solo_metadata.get("total_notes", 0),
                analysis_coverage=coverage,
                scale_insights=self._as_str_list(insights.get("scale_insights")),
                arpeggio_insights=self._as_str_list(insights.get("arpeggio_insights")),
                approach_insights=self._as_str_list(insights.get("approach_insights")),
                overall_character=str(
                    insights.get("overall_character") or "Unable to assess character"
                ),
                technical_level=str(
                    insights.get("technical_level") or "Unable to assess level"
                ),
                harmonic_sophistication=str(
                    insights.get("harmonic_sophistication")
                    or "Unable to assess harmonic sophistication"
                ),
                melodic_characteristics=self._as_str_list(
                    insights.get("melodic_characteristics")
                ),
                recommendations=self._as_str_list(insights.get("recommendations")),
            )
        except Exception as exc:
            logger.warning("OpenAI analysis failed: %s", exc)
            if not use_fallback_on_error:
                raise OpenAIAnalysisError(str(exc)) from exc
            print(f"OpenAI analysis failed ({exc}). Falling back to rule-based summary.")
            return self.fallback_generator.generate_summary(
                scale_analysis, arpeggio_analysis, approach_analysis, solo_metadata
            )

    def _request_insights(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        client = self._get_client()
        user_content = (
            "Analyze this jazz solo using only the structured detector findings below.\n\n"
            + json.dumps(payload, indent=2)
        )

        response = client.chat.completions.create(
            model=self.model,
            temperature=0.4,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
        )

        content = response.choices[0].message.content
        if not content:
            raise OpenAIAnalysisError("Empty response from OpenAI")

        try:
            data = json.loads(content)
        except json.JSONDecodeError as exc:
            raise OpenAIAnalysisError(f"Invalid JSON from OpenAI: {exc}") from exc

        if not isinstance(data, dict):
            raise OpenAIAnalysisError("OpenAI response was not a JSON object")
        return data

    @staticmethod
    def _as_str_list(value: Any) -> List[str]:
        if value is None:
            return []
        if isinstance(value, str):
            return [value] if value.strip() else []
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        return [str(value)]
