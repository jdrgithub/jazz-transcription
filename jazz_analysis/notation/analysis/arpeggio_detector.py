"""
Jazz arpeggio detection engine for analyzing chord patterns in solo data.
"""

import logging
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass
from collections import Counter, defaultdict
import math

logger = logging.getLogger(__name__)

try:
    from music21 import pitch, chord, interval
    MUSIC21_AVAILABLE = True
except ImportError:
    MUSIC21_AVAILABLE = False
    logger.warning("music21 not available. Install with: pip install music21")


@dataclass
class ArpeggioPattern:
    """Represents a detected arpeggio pattern."""
    name: str
    root: str
    chord_type: str
    pitches: List[int]  # MIDI pitch numbers in order
    confidence: float  # 0.0 to 1.0
    start_time: float
    end_time: float
    direction: str  # 'ascending', 'descending', 'mixed'
    notes_used: List[int]  # Indices of notes that form this arpeggio
    octave_span: int  # Number of octaves spanned


@dataclass
class ArpeggioAnalysis:
    """Results of arpeggio analysis on a solo."""
    detected_arpeggios: List[ArpeggioPattern]
    chord_progression: List[Tuple[str, float]]  # (chord_name, time)
    most_common_arpeggios: List[Tuple[str, int]] = None
    arpeggio_coverage: float = 0.0  # Percentage of notes covered by detected arpeggios


class JazzArpeggioDetector:
    """Detects jazz arpeggios and chord patterns in solo data."""
    
    def __init__(self):
        """Initialize the jazz arpeggio detector."""
        if not MUSIC21_AVAILABLE:
            raise ImportError("music21 is required for arpeggio detection. Install with: pip install music21")
        
        # Define common jazz chord types with their interval patterns
        self.jazz_chords = {
            # Triads
            'Major': [0, 4, 7],
            'Minor': [0, 3, 7],
            'Diminished': [0, 3, 6],
            'Augmented': [0, 4, 8],
            
            # 7th Chords
            'Major 7': [0, 4, 7, 11],
            'Minor 7': [0, 3, 7, 10],
            'Dominant 7': [0, 4, 7, 10],
            'Minor 7b5': [0, 3, 6, 10],
            'Diminished 7': [0, 3, 6, 9],
            'Major 7#5': [0, 4, 8, 11],
            'Minor Major 7': [0, 3, 7, 11],
            
            # Extended Chords
            'Major 9': [0, 4, 7, 11, 2],
            'Minor 9': [0, 3, 7, 10, 2],
            'Dominant 9': [0, 4, 7, 10, 2],
            'Major 11': [0, 4, 7, 11, 2, 5],
            'Minor 11': [0, 3, 7, 10, 2, 5],
            'Dominant 11': [0, 4, 7, 10, 2, 5],
            'Major 13': [0, 4, 7, 11, 2, 5, 9],
            'Minor 13': [0, 3, 7, 10, 2, 5, 9],
            'Dominant 13': [0, 4, 7, 10, 2, 5, 9],
            
            # Altered Chords
            'Dominant 7#9': [0, 4, 7, 10, 3],
            'Dominant 7b9': [0, 4, 7, 10, 1],
            'Dominant 7#11': [0, 4, 7, 10, 6],
            'Dominant 7b13': [0, 4, 7, 10, 8],
            
            # Sus Chords
            'Sus 2': [0, 2, 7],
            'Sus 4': [0, 5, 7],
            '7Sus 4': [0, 5, 7, 10],
        }
    
    def analyze_notes(self, notes: List[Dict], min_arpeggio_length: int = 3) -> ArpeggioAnalysis:
        """
        Analyze notes to detect jazz arpeggios and chord patterns.
        
        Args:
            notes: List of note dictionaries with 'pitch' and 'onset' keys
            min_arpeggio_length: Minimum number of notes to consider an arpeggio
            
        Returns:
            ArpeggioAnalysis object with detected arpeggios and patterns
        """
        if not notes:
            return ArpeggioAnalysis(detected_arpeggios=[], chord_progression=[])
        
        logger.info(f"Analyzing {len(notes)} notes for jazz arpeggios")
        
        detected_arpeggios = []
        
        # Find potential arpeggio sequences
        arpeggio_sequences = self._find_arpeggio_sequences(notes, min_arpeggio_length)
        
        # Analyze each sequence for chord patterns
        for sequence in arpeggio_sequences:
            arpeggios = self._detect_arpeggios_in_sequence(sequence, notes)
            detected_arpeggios.extend(arpeggios)
        
        # Remove duplicates and sort by confidence
        detected_arpeggios = self._remove_duplicate_arpeggios(detected_arpeggios)
        detected_arpeggios.sort(key=lambda x: x.confidence, reverse=True)
        
        # Analyze chord progression
        chord_progression = self._analyze_chord_progression(notes)
        
        # Calculate statistics
        most_common_arpeggios = self._get_most_common_arpeggios(detected_arpeggios)
        arpeggio_coverage = self._calculate_arpeggio_coverage(notes, detected_arpeggios)
        
        return ArpeggioAnalysis(
            detected_arpeggios=detected_arpeggios,
            chord_progression=chord_progression,
            most_common_arpeggios=most_common_arpeggios,
            arpeggio_coverage=arpeggio_coverage
        )
    
    def _find_arpeggio_sequences(self, notes: List[Dict], min_length: int) -> List[List[int]]:
        """Find potential arpeggio sequences in the notes."""
        sequences = []
        
        # Look for sequences of notes that could form arpeggios
        i = 0
        while i < len(notes) - min_length + 1:
            sequence = [i]
            
            # Extend sequence while notes are reasonably close in time
            j = i + 1
            while j < len(notes):
                time_gap = notes[j]['onset'] - notes[j-1]['onset']
                
                # If notes are too far apart, break the sequence
                if time_gap > 2.0:  # 2 beats maximum gap
                    break
                
                sequence.append(j)
                j += 1
            
            # Only consider sequences of minimum length
            if len(sequence) >= min_length:
                sequences.append(sequence)
            
            # Move to next potential start
            i += 1
        
        return sequences
    
    def _detect_arpeggios_in_sequence(self, sequence: List[int], notes: List[Dict]) -> List[ArpeggioPattern]:
        """Detect arpeggios in a sequence of note indices."""
        if len(sequence) < 3:
            return []
        
        sequence_notes = [notes[i] for i in sequence]
        sequence_pitches = [note['pitch'] for note in sequence_notes]
        
        detected_arpeggios = []
        
        # Try each possible root note
        for root_pitch_class in range(12):
            root_midi = root_pitch_class
            
            # Try each chord type
            for chord_name, chord_intervals in self.jazz_chords.items():
                # Generate chord pitches from root
                chord_pitches = [(root_midi + interval) % 12 for interval in chord_intervals]
                
                # Check if sequence pitches match chord structure
                matching_notes = []
                for i, pitch in enumerate(sequence_pitches):
                    pitch_class = pitch % 12
                    if pitch_class in chord_pitches:
                        matching_notes.append(i)
                
                # Calculate confidence based on how many notes match
                if len(matching_notes) >= 3:  # At least 3 notes must match
                    confidence = len(matching_notes) / len(sequence_pitches)
                    
                    # Check if notes are in arpeggio order (ascending/descending)
                    direction = self._determine_arpeggio_direction(sequence_pitches)
                    
                    # Calculate octave span
                    octave_span = self._calculate_octave_span(sequence_pitches)
                    
                    # Only consider if confidence is reasonable
                    if confidence >= 0.6:  # At least 60% of notes match
                        # Convert root to note name
                        root_name = pitch.Pitch(root_pitch_class).name
                        
                        # Calculate time span
                        start_time = min(sequence_notes[i]['onset'] for i in matching_notes)
                        end_time = max(sequence_notes[i]['onset'] for i in matching_notes)
                        
                        arpeggio_pattern = ArpeggioPattern(
                            name=f"{root_name} {chord_name}",
                            root=root_name,
                            chord_type=chord_name,
                            pitches=sequence_pitches,
                            confidence=confidence,
                            start_time=start_time,
                            end_time=end_time,
                            direction=direction,
                            notes_used=[sequence[i] for i in matching_notes],
                            octave_span=octave_span
                        )
                        
                        detected_arpeggios.append(arpeggio_pattern)
        
        return detected_arpeggios
    
    def _determine_arpeggio_direction(self, pitches: List[int]) -> str:
        """Determine if arpeggio is ascending, descending, or mixed."""
        if len(pitches) < 2:
            return 'mixed'
        
        ascending_count = 0
        descending_count = 0
        
        for i in range(1, len(pitches)):
            if pitches[i] > pitches[i-1]:
                ascending_count += 1
            elif pitches[i] < pitches[i-1]:
                descending_count += 1
        
        if ascending_count > descending_count:
            return 'ascending'
        elif descending_count > ascending_count:
            return 'descending'
        else:
            return 'mixed'
    
    def _calculate_octave_span(self, pitches: List[int]) -> int:
        """Calculate the number of octaves spanned by the arpeggio."""
        if not pitches:
            return 0
        
        min_pitch = min(pitches)
        max_pitch = max(pitches)
        
        # Calculate octave difference
        min_octave = min_pitch // 12
        max_octave = max_pitch // 12
        
        return max_octave - min_octave + 1
    
    def _analyze_chord_progression(self, notes: List[Dict]) -> List[Tuple[str, float]]:
        """Analyze chord progression from the notes."""
        # This is a simplified chord progression analysis
        # In a full implementation, this would analyze harmonic rhythm and chord changes
        
        chord_progression = []
        
        # Group notes by time windows to identify chords
        time_windows = self._create_time_windows(notes, window_size=1.0)  # 1 beat windows
        
        for window_start, window_notes in time_windows.items():
            if len(window_notes) >= 3:  # Need at least 3 notes for a chord
                chord_name = self._identify_chord_from_notes(window_notes)
                if chord_name:
                    chord_progression.append((chord_name, window_start))
        
        return chord_progression
    
    def _create_time_windows(self, notes: List[Dict], window_size: float) -> Dict[float, List[Dict]]:
        """Create time windows for chord analysis."""
        windows = defaultdict(list)
        
        for note in notes:
            window_start = math.floor(note['onset'] / window_size) * window_size
            windows[window_start].append(note)
        
        return dict(windows)
    
    def _identify_chord_from_notes(self, notes: List[Dict]) -> Optional[str]:
        """Identify chord type from a group of notes."""
        if len(notes) < 3:
            return None
        
        pitch_classes = [note['pitch'] % 12 for note in notes]
        pitch_classes = sorted(list(set(pitch_classes)))  # Remove duplicates and sort
        
        # Try to match against known chord patterns
        for chord_name, chord_intervals in self.jazz_chords.items():
            if self._pitch_classes_match_chord(pitch_classes, chord_intervals):
                # Find the root note
                root_pitch_class = self._find_chord_root(pitch_classes, chord_intervals)
                if root_pitch_class is not None:
                    root_name = pitch.Pitch(root_pitch_class).name
                    return f"{root_name} {chord_name}"
        
        return None
    
    def _pitch_classes_match_chord(self, pitch_classes: List[int], chord_intervals: List[int]) -> bool:
        """Check if pitch classes match a chord pattern."""
        if len(pitch_classes) < len(chord_intervals):
            return False
        
        # Try each possible root
        for root in range(12):
            chord_pitches = [(root + interval) % 12 for interval in chord_intervals]
            if all(pc in pitch_classes for pc in chord_pitches):
                return True
        
        return False
    
    def _find_chord_root(self, pitch_classes: List[int], chord_intervals: List[int]) -> Optional[int]:
        """Find the root note of a chord."""
        for root in range(12):
            chord_pitches = [(root + interval) % 12 for interval in chord_intervals]
            if all(pc in pitch_classes for pc in chord_pitches):
                return root
        return None
    
    def _get_most_common_arpeggios(self, detected_arpeggios: List[ArpeggioPattern]) -> List[Tuple[str, int]]:
        """Get the most commonly detected arpeggios."""
        arpeggio_counts = Counter(arpeggio.name for arpeggio in detected_arpeggios)
        return arpeggio_counts.most_common(5)
    
    def _calculate_arpeggio_coverage(self, notes: List[Dict], detected_arpeggios: List[ArpeggioPattern]) -> float:
        """Calculate what percentage of notes are covered by detected arpeggios."""
        if not notes or not detected_arpeggios:
            return 0.0
        
        covered_notes = set()
        for arpeggio in detected_arpeggios:
            for note_idx in arpeggio.notes_used:
                if note_idx < len(notes):
                    covered_notes.add(note_idx)
        
        return len(covered_notes) / len(notes) * 100.0
    
    def _remove_duplicate_arpeggios(self, arpeggios: List[ArpeggioPattern]) -> List[ArpeggioPattern]:
        """Remove duplicate or very similar arpeggios."""
        if not arpeggios:
            return []
        
        unique_arpeggios = []
        for arpeggio in arpeggios:
            # Check if this arpeggio is too similar to an existing one
            is_duplicate = False
            for existing in unique_arpeggios:
                if (arpeggio.name == existing.name and 
                    abs(arpeggio.start_time - existing.start_time) < 0.5 and
                    abs(arpeggio.confidence - existing.confidence) < 0.1):
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_arpeggios.append(arpeggio)
        
        return unique_arpeggios
    
    def export_analysis(self, analysis: ArpeggioAnalysis, output_path: str) -> None:
        """
        Export arpeggio analysis results to a text file.
        
        Args:
            analysis: ArpeggioAnalysis object to export
            output_path: Path to save the analysis file
        """
        with open(output_path, 'w') as f:
            f.write("Jazz Arpeggio Analysis Results\n")
            f.write("=" * 50 + "\n\n")
            
            # Write arpeggio coverage
            f.write(f"Arpeggio Coverage: {analysis.arpeggio_coverage:.1f}% of notes\n\n")
            
            # Write most common arpeggios
            if analysis.most_common_arpeggios:
                f.write("Most Common Arpeggios:\n")
                for arpeggio_name, count in analysis.most_common_arpeggios:
                    f.write(f"  {arpeggio_name}: {count} occurrences\n")
                f.write("\n")
            
            # Write chord progression
            if analysis.chord_progression:
                f.write("Chord Progression:\n")
                for chord_name, time in analysis.chord_progression:
                    f.write(f"  {time:.2f}: {chord_name}\n")
                f.write("\n")
            
            # Write detailed arpeggio detections
            f.write(f"Detected Arpeggio Patterns ({len(analysis.detected_arpeggios)} total):\n")
            f.write(f"{'Arpeggio':<25} {'Direction':<12} {'Confidence':<12} {'Time Range':<15} {'Octaves':<8}\n")
            f.write(f"{'-' * 80}\n")
            
            for arpeggio in analysis.detected_arpeggios:
                time_range = f"{arpeggio.start_time:.2f}-{arpeggio.end_time:.2f}"
                f.write(f"{arpeggio.name:<25} {arpeggio.direction:<12} "
                       f"{arpeggio.confidence:<12.2f} {time_range:<15} {arpeggio.octave_span:<8}\n")
            
            # Write detailed arpeggio information
            f.write(f"\nDetailed Arpeggio Information:\n")
            f.write(f"{'-' * 50}\n")
            
            for i, arpeggio in enumerate(analysis.detected_arpeggios, 1):
                f.write(f"\n{i}. {arpeggio.name}\n")
                f.write(f"   Direction: {arpeggio.direction}\n")
                f.write(f"   Confidence: {arpeggio.confidence:.2f}\n")
                f.write(f"   Time Range: {arpeggio.start_time:.2f} - {arpeggio.end_time:.2f}\n")
                f.write(f"   Octave Span: {arpeggio.octave_span}\n")
                f.write(f"   Notes Used: {len(arpeggio.notes_used)}\n")
                f.write(f"   Pitches: {arpeggio.pitches}\n")
        
        logger.info(f"Exported arpeggio analysis to: {output_path}")
