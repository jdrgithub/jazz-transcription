"""
Jazz approach tone detection engine for analyzing chromatic and neighbor tone patterns in solo data.
"""

import logging
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass
from collections import Counter, defaultdict
import math

logger = logging.getLogger(__name__)

try:
    from music21 import pitch, interval
    MUSIC21_AVAILABLE = True
except ImportError:
    MUSIC21_AVAILABLE = False
    logger.warning("music21 not available. Install with: pip install music21")


@dataclass
class ApproachPattern:
    """Represents a detected approach tone pattern."""
    name: str
    target_note: int  # MIDI pitch of target note
    approach_notes: List[int]  # MIDI pitches of approach notes
    pattern_type: str  # 'chromatic', 'diatonic', 'enclosure', 'diminished_burst'
    direction: str  # 'above', 'below', 'mixed'
    confidence: float  # 0.0 to 1.0
    start_time: float
    end_time: float
    notes_used: List[int]  # Indices of notes that form this pattern
    resolution_strength: float  # How well it resolves to target


@dataclass
class ApproachAnalysis:
    """Results of approach tone analysis on a solo."""
    detected_patterns: List[ApproachPattern]
    target_notes: List[Tuple[int, int]]  # (target_pitch, frequency)
    most_common_patterns: List[Tuple[str, int]] = None
    approach_coverage: float = 0.0  # Percentage of notes involved in approach patterns


class JazzApproachDetector:
    """Detects jazz approach tones and chromatic patterns in solo data."""
    
    def __init__(self):
        """Initialize the jazz approach tone detector."""
        if not MUSIC21_AVAILABLE:
            raise ImportError("music21 is required for approach tone detection. Install with: pip install music21")
        
        # Define approach tone patterns
        self.approach_patterns = {
            # Single chromatic approaches
            'Chromatic Above': [1],  # Semitone above
            'Chromatic Below': [-1],  # Semitone below
            
            # Double chromatic approaches
            'Double Chromatic Above': [2, 1],  # Whole tone then semitone above
            'Double Chromatic Below': [-2, -1],  # Whole tone then semitone below
            
            # Enclosures (chromatic from both sides)
            'Enclosure Above-Below': [1, -1],  # Above then below
            'Enclosure Below-Above': [-1, 1],  # Below then above
            
            # Diatonic approaches
            'Diatonic Step Above': [2],  # Diatonic step above
            'Diatonic Step Below': [-2],  # Diatonic step below
            
            # Diminished patterns
            'Diminished Burst': [3, 6, 9],  # Minor third intervals
            'Diminished Approach': [3, -1],  # Minor third then semitone
            
            # Bebop approaches
            'Bebop Enclosure': [1, -2, 1],  # Above, below, above
            'Bebop Approach': [2, 1, -1],  # Diatonic, chromatic, chromatic
        }
    
    def analyze_notes(self, notes: List[Dict], chord_progression: List[Tuple[str, float]] = None) -> ApproachAnalysis:
        """
        Analyze notes to detect jazz approach tone patterns.
        
        Args:
            notes: List of note dictionaries with 'pitch' and 'onset' keys
            chord_progression: Optional chord progression for context
            
        Returns:
            ApproachAnalysis object with detected approach patterns
        """
        if not notes:
            return ApproachAnalysis(detected_patterns=[], target_notes=[])
        
        logger.info(f"Analyzing {len(notes)} notes for jazz approach tones")
        
        detected_patterns = []
        
        # Find potential target notes (chord tones, strong beats, etc.)
        target_notes = self._identify_target_notes(notes, chord_progression)
        
        # Analyze approach patterns to each target note
        for target_idx, target_note in target_notes:
            patterns = self._detect_approaches_to_target(target_idx, notes)
            detected_patterns.extend(patterns)
        
        # Remove duplicates and sort by confidence
        detected_patterns = self._remove_duplicate_patterns(detected_patterns)
        detected_patterns.sort(key=lambda x: x.confidence, reverse=True)
        
        # Calculate statistics
        target_frequencies = self._get_target_frequencies(detected_patterns)
        most_common_patterns = self._get_most_common_patterns(detected_patterns)
        approach_coverage = self._calculate_approach_coverage(notes, detected_patterns)
        
        return ApproachAnalysis(
            detected_patterns=detected_patterns,
            target_notes=target_frequencies,
            most_common_patterns=most_common_patterns,
            approach_coverage=approach_coverage
        )
    
    def _identify_target_notes(self, notes: List[Dict], chord_progression: List[Tuple[str, float]] = None) -> List[Tuple[int, Dict]]:
        """Identify potential target notes for approach tone analysis."""
        target_notes = []
        
        # Strategy 1: Strong beats (every 4th note, or notes on beat 1)
        for i, note in enumerate(notes):
            if i % 4 == 0 or self._is_strong_beat(note['onset']):
                target_notes.append((i, note))
        
        # Strategy 2: Chord tones if chord progression is available
        if chord_progression:
            chord_targets = self._find_chord_tone_targets(notes, chord_progression)
            target_notes.extend(chord_targets)
        
        # Strategy 3: Long notes (likely targets)
        for i, note in enumerate(notes):
            if note.get('duration', 0) > 1.0:  # Notes longer than 1 beat
                target_notes.append((i, note))
        
        # Remove duplicates and sort by time
        unique_targets = {}
        for idx, note in target_notes:
            if idx not in unique_targets:
                unique_targets[idx] = note
        
        return sorted(unique_targets.items())
    
    def _is_strong_beat(self, onset: float) -> bool:
        """Check if a note is on a strong beat."""
        # Check if onset is close to a beat (assuming 4/4 time)
        beat_position = onset % 4.0
        return abs(beat_position) < 0.1 or abs(beat_position - 1.0) < 0.1
    
    def _find_chord_tone_targets(self, notes: List[Dict], chord_progression: List[Tuple[str, float]]) -> List[Tuple[int, Dict]]:
        """Find notes that are chord tones based on chord progression."""
        chord_targets = []
        
        for i, note in enumerate(notes):
            # Find the chord at this time
            current_chord = self._get_chord_at_time(note['onset'], chord_progression)
            if current_chord:
                # Check if this note is a chord tone
                if self._is_chord_tone(note['pitch'], current_chord):
                    chord_targets.append((i, note))
        
        return chord_targets
    
    def _get_chord_at_time(self, time: float, chord_progression: List[Tuple[str, float]]) -> Optional[str]:
        """Get the chord at a specific time."""
        if not chord_progression:
            return None
        
        # Find the most recent chord before or at this time
        for chord_name, chord_time in reversed(chord_progression):
            if chord_time <= time:
                return chord_name
        
        return chord_progression[0][0] if chord_progression else None
    
    def _is_chord_tone(self, pitch: int, chord_name: str) -> bool:
        """Check if a pitch is a chord tone for the given chord."""
        # Simplified chord tone detection
        # In a full implementation, this would parse chord names and check intervals
        
        # For now, assume major chords and check basic intervals
        pitch_class = pitch % 12
        
        # Basic major chord tones (root, third, fifth)
        if 'major' in chord_name.lower() or 'maj' in chord_name.lower():
            # This is simplified - would need proper chord parsing
            return True
        
        return False
    
    def _detect_approaches_to_target(self, target_idx: int, notes: List[Dict]) -> List[ApproachPattern]:
        """Detect approach patterns leading to a target note."""
        if target_idx >= len(notes):
            return []
        
        target_note = notes[target_idx]
        target_pitch = target_note['pitch']
        target_time = target_note['onset']
        
        detected_patterns = []
        
        # Look for approach notes before the target (within 2 beats)
        approach_window = 2.0  # 2 beats before target
        start_idx = max(0, target_idx - 10)  # Look back up to 10 notes
        
        for i in range(start_idx, target_idx):
            if target_time - notes[i]['onset'] > approach_window:
                continue
            
            # Try each approach pattern
            for pattern_name, intervals in self.approach_patterns.items():
                pattern = self._check_approach_pattern(
                    i, target_idx, notes, target_pitch, intervals, pattern_name
                )
                if pattern:
                    detected_patterns.append(pattern)
        
        return detected_patterns
    
    def _check_approach_pattern(self, start_idx: int, target_idx: int, notes: List[Dict], 
                               target_pitch: int, intervals: List[int], pattern_name: str) -> Optional[ApproachPattern]:
        """Check if a sequence of notes matches an approach pattern."""
        if start_idx + len(intervals) > target_idx:
            return None
        
        # Get the sequence of notes
        sequence_notes = []
        for i in range(len(intervals)):
            note_idx = start_idx + i
            if note_idx < len(notes):
                sequence_notes.append(notes[note_idx])
            else:
                return None
        
        # Check if the sequence matches the pattern
        expected_pitches = [target_pitch - interval for interval in intervals]
        actual_pitches = [note['pitch'] for note in sequence_notes]
        
        # Allow for octave differences
        matches = 0
        for expected, actual in zip(expected_pitches, actual_pitches):
            if abs(expected - actual) % 12 == 0:  # Same pitch class
                matches += 1
        
        confidence = matches / len(intervals)
        
        if confidence >= 0.8:  # At least 80% of notes match
            # Determine direction
            direction = self._determine_approach_direction(actual_pitches, target_pitch)
            
            # Calculate resolution strength
            resolution_strength = self._calculate_resolution_strength(sequence_notes, target_pitch)
            
            # Calculate time span
            start_time = sequence_notes[0]['onset']
            end_time = sequence_notes[-1]['onset']
            
            return ApproachPattern(
                name=pattern_name,
                target_note=target_pitch,
                approach_notes=actual_pitches,
                pattern_type=self._get_pattern_type(pattern_name),
                direction=direction,
                confidence=confidence,
                start_time=start_time,
                end_time=end_time,
                notes_used=list(range(start_idx, start_idx + len(intervals))),
                resolution_strength=resolution_strength
            )
        
        return None
    
    def _determine_approach_direction(self, approach_pitches: List[int], target_pitch: int) -> str:
        """Determine the direction of approach (above, below, mixed)."""
        above_count = 0
        below_count = 0
        
        for pitch in approach_pitches:
            if pitch > target_pitch:
                above_count += 1
            elif pitch < target_pitch:
                below_count += 1
        
        if above_count > below_count:
            return 'above'
        elif below_count > above_count:
            return 'below'
        else:
            return 'mixed'
    
    def _get_pattern_type(self, pattern_name: str) -> str:
        """Get the general type of approach pattern."""
        if 'chromatic' in pattern_name.lower():
            return 'chromatic'
        elif 'diatonic' in pattern_name.lower():
            return 'diatonic'
        elif 'enclosure' in pattern_name.lower():
            return 'enclosure'
        elif 'diminished' in pattern_name.lower():
            return 'diminished'
        elif 'bebop' in pattern_name.lower():
            return 'bebop'
        else:
            return 'other'
    
    def _calculate_resolution_strength(self, approach_notes: List[Dict], target_pitch: int) -> float:
        """Calculate how strongly the approach resolves to the target."""
        if not approach_notes:
            return 0.0
        
        # Check if the last approach note is close to the target
        last_note_pitch = approach_notes[-1]['pitch']
        interval_to_target = abs(last_note_pitch - target_pitch) % 12
        
        # Stronger resolution for smaller intervals
        if interval_to_target == 1:  # Semitone
            return 1.0
        elif interval_to_target == 2:  # Whole tone
            return 0.8
        elif interval_to_target == 3:  # Minor third
            return 0.6
        else:
            return 0.4
    
    def _get_target_frequencies(self, detected_patterns: List[ApproachPattern]) -> List[Tuple[int, int]]:
        """Get frequency of each target note."""
        target_counts = Counter(pattern.target_note for pattern in detected_patterns)
        return target_counts.most_common(10)
    
    def _get_most_common_patterns(self, detected_patterns: List[ApproachPattern]) -> List[Tuple[str, int]]:
        """Get the most commonly detected approach patterns."""
        pattern_counts = Counter(pattern.name for pattern in detected_patterns)
        return pattern_counts.most_common(5)
    
    def _calculate_approach_coverage(self, notes: List[Dict], detected_patterns: List[ApproachPattern]) -> float:
        """Calculate what percentage of notes are involved in approach patterns."""
        if not notes or not detected_patterns:
            return 0.0
        
        covered_notes = set()
        for pattern in detected_patterns:
            for note_idx in pattern.notes_used:
                if note_idx < len(notes):
                    covered_notes.add(note_idx)
        
        return len(covered_notes) / len(notes) * 100.0
    
    def _remove_duplicate_patterns(self, patterns: List[ApproachPattern]) -> List[ApproachPattern]:
        """Remove duplicate or very similar approach patterns."""
        if not patterns:
            return []
        
        unique_patterns = []
        for pattern in patterns:
            # Check if this pattern is too similar to an existing one
            is_duplicate = False
            for existing in unique_patterns:
                if (pattern.name == existing.name and 
                    pattern.target_note == existing.target_note and
                    abs(pattern.start_time - existing.start_time) < 0.5):
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_patterns.append(pattern)
        
        return unique_patterns
    
    def export_analysis(self, analysis: ApproachAnalysis, output_path: str) -> None:
        """
        Export approach tone analysis results to a text file.
        
        Args:
            analysis: ApproachAnalysis object to export
            output_path: Path to save the analysis file
        """
        with open(output_path, 'w') as f:
            f.write("Jazz Approach Tone Analysis Results\n")
            f.write("=" * 50 + "\n\n")
            
            # Write approach coverage
            f.write(f"Approach Coverage: {analysis.approach_coverage:.1f}% of notes\n\n")
            
            # Write most common patterns
            if analysis.most_common_patterns:
                f.write("Most Common Approach Patterns:\n")
                for pattern_name, count in analysis.most_common_patterns:
                    f.write(f"  {pattern_name}: {count} occurrences\n")
                f.write("\n")
            
            # Write target note frequencies
            if analysis.target_notes:
                f.write("Most Targeted Notes:\n")
                for target_pitch, frequency in analysis.target_notes:
                    note_name = pitch.Pitch(target_pitch).name
                    f.write(f"  {note_name} ({target_pitch}): {frequency} times\n")
                f.write("\n")
            
            # Write detailed approach detections
            f.write(f"Detected Approach Patterns ({len(analysis.detected_patterns)} total):\n")
            f.write(f"{'Pattern':<25} {'Type':<12} {'Direction':<10} {'Confidence':<12} {'Resolution':<12} {'Time Range':<15}\n")
            f.write(f"{'-' * 90}\n")
            
            for pattern in analysis.detected_patterns:
                time_range = f"{pattern.start_time:.2f}-{pattern.end_time:.2f}"
                f.write(f"{pattern.name:<25} {pattern.pattern_type:<12} {pattern.direction:<10} "
                       f"{pattern.confidence:<12.2f} {pattern.resolution_strength:<12.2f} {time_range:<15}\n")
            
            # Write detailed pattern information
            f.write(f"\nDetailed Pattern Information:\n")
            f.write(f"{'-' * 50}\n")
            
            for i, pattern in enumerate(analysis.detected_patterns, 1):
                target_name = pitch.Pitch(pattern.target_note).name
                approach_names = [pitch.Pitch(p).name for p in pattern.approach_notes]
                
                f.write(f"\n{i}. {pattern.name}\n")
                f.write(f"   Target Note: {target_name} ({pattern.target_note})\n")
                f.write(f"   Approach Notes: {', '.join(approach_names)}\n")
                f.write(f"   Type: {pattern.pattern_type}\n")
                f.write(f"   Direction: {pattern.direction}\n")
                f.write(f"   Confidence: {pattern.confidence:.2f}\n")
                f.write(f"   Resolution Strength: {pattern.resolution_strength:.2f}\n")
                f.write(f"   Time Range: {pattern.start_time:.2f} - {pattern.end_time:.2f}\n")
                f.write(f"   Notes Used: {len(pattern.notes_used)}\n")
        
        logger.info(f"Exported approach tone analysis to: {output_path}")
