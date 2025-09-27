"""
Jazz scale detection engine for analyzing patterns in solo data.
"""

import logging
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass
from collections import Counter, defaultdict

logger = logging.getLogger(__name__)

try:
    from music21 import pitch, scale, key, interval
    MUSIC21_AVAILABLE = True
except ImportError:
    MUSIC21_AVAILABLE = False
    logger.warning("music21 not available. Install with: pip install music21")


@dataclass
class ScalePattern:
    """Represents a detected scale pattern."""
    name: str
    root: str
    pitches: List[int]  # MIDI pitch numbers
    confidence: float  # 0.0 to 1.0
    start_time: float
    end_time: float
    notes_used: List[int]  # Indices of notes that match this scale


@dataclass
class ScaleAnalysis:
    """Results of scale analysis on a solo."""
    detected_scales: List[ScalePattern]
    key_signature: Optional[str] = None
    most_common_scales: List[Tuple[str, int]] = None
    scale_coverage: float = 0.0  # Percentage of notes covered by detected scales


class JazzScaleDetector:
    """Detects jazz scales and patterns in solo data."""
    
    def __init__(self):
        """Initialize the jazz scale detector."""
        if not MUSIC21_AVAILABLE:
            raise ImportError("music21 is required for scale detection. Install with: pip install music21")
        
        # Define common jazz scales with their interval patterns
        self.jazz_scales = {
            # Major scales and modes
            'Major': [0, 2, 4, 5, 7, 9, 11],
            'Dorian': [0, 2, 3, 5, 7, 9, 10],
            'Phrygian': [0, 1, 3, 5, 7, 8, 10],
            'Lydian': [0, 2, 4, 6, 7, 9, 11],
            'Mixolydian': [0, 2, 4, 5, 7, 9, 10],
            'Aeolian': [0, 2, 3, 5, 7, 8, 10],
            'Locrian': [0, 1, 3, 5, 6, 8, 10],
            
            # Minor scales
            'Harmonic Minor': [0, 2, 3, 5, 7, 8, 11],
            'Melodic Minor': [0, 2, 3, 5, 7, 9, 11],
            'Natural Minor': [0, 2, 3, 5, 7, 8, 10],
            
            # Diminished scales
            'Half-Diminished': [0, 2, 3, 5, 6, 8, 10],
            'Whole-Half Diminished': [0, 2, 3, 5, 6, 8, 9, 11],
            'Half-Whole Diminished': [0, 1, 3, 4, 6, 7, 9, 10],
            
            # Bebop scales
            'Bebop Major': [0, 2, 4, 5, 7, 8, 9, 11],
            'Bebop Dominant': [0, 2, 4, 5, 7, 9, 10, 11],
            'Bebop Minor': [0, 2, 3, 5, 7, 8, 9, 10],
            
            # Pentatonic scales
            'Major Pentatonic': [0, 2, 4, 7, 9],
            'Minor Pentatonic': [0, 3, 5, 7, 10],
            'Blues Scale': [0, 3, 5, 6, 7, 10],
            
            # Other jazz scales
            'Whole Tone': [0, 2, 4, 6, 8, 10],
            'Chromatic': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
            'Altered': [0, 1, 3, 4, 6, 8, 10],
            'Lydian Dominant': [0, 2, 4, 6, 7, 9, 10],
        }
    
    def analyze_notes(self, notes: List[Dict], window_size: int = 8) -> ScaleAnalysis:
        """
        Analyze notes to detect jazz scales and patterns.
        
        Args:
            notes: List of note dictionaries with 'pitch' and 'onset' keys
            window_size: Number of notes to analyze in each window
            
        Returns:
            ScaleAnalysis object with detected scales and patterns
        """
        if not notes:
            return ScaleAnalysis(detected_scales=[])
        
        logger.info(f"Analyzing {len(notes)} notes for jazz scales")
        
        detected_scales = []
        all_pitches = [note['pitch'] for note in notes]
        
        # Analyze in sliding windows
        for i in range(0, len(notes) - window_size + 1, window_size // 2):
            window_notes = notes[i:i + window_size]
            window_pitches = [note['pitch'] for note in window_notes]
            
            # Detect scales in this window
            window_scales = self._detect_scales_in_window(window_pitches, window_notes)
            detected_scales.extend(window_scales)
        
        # Analyze entire solo for overall key
        key_signature = self._detect_key_signature(all_pitches)
        
        # Calculate statistics
        most_common_scales = self._get_most_common_scales(detected_scales)
        scale_coverage = self._calculate_scale_coverage(notes, detected_scales)
        
        return ScaleAnalysis(
            detected_scales=detected_scales,
            key_signature=key_signature,
            most_common_scales=most_common_scales,
            scale_coverage=scale_coverage
        )
    
    def _detect_scales_in_window(self, pitches: List[int], notes: List[Dict]) -> List[ScalePattern]:
        """Detect scales in a window of notes."""
        if len(pitches) < 3:  # Need at least 3 notes to detect a scale
            return []
        
        detected_scales = []
        pitch_classes = [p % 12 for p in pitches]  # Convert to pitch classes
        
        # Try each possible root note
        for root_pitch_class in range(12):
            root_midi = root_pitch_class
            
            # Try each scale type
            for scale_name, scale_intervals in self.jazz_scales.items():
                # Generate scale pitches from root
                scale_pitches = [(root_midi + interval) % 12 for interval in scale_intervals]
                
                # Calculate how many notes match this scale
                matching_notes = sum(1 for pc in pitch_classes if pc in scale_pitches)
                confidence = matching_notes / len(pitch_classes)
                
                # Only consider scales with reasonable confidence
                if confidence >= 0.6:  # At least 60% of notes match
                    # Find which notes match this scale
                    matching_indices = [i for i, pc in enumerate(pitch_classes) if pc in scale_pitches]
                    
                    # Calculate time span
                    start_time = min(notes[i]['onset'] for i in matching_indices)
                    end_time = max(notes[i]['onset'] for i in matching_indices)
                    
                    # Convert root to note name
                    root_name = pitch.Pitch(root_pitch_class).name
                    
                    scale_pattern = ScalePattern(
                        name=scale_name,
                        root=root_name,
                        pitches=scale_pitches,
                        confidence=confidence,
                        start_time=start_time,
                        end_time=end_time,
                        notes_used=matching_indices
                    )
                    
                    detected_scales.append(scale_pattern)
        
        # Sort by confidence and remove duplicates
        detected_scales.sort(key=lambda x: x.confidence, reverse=True)
        return self._remove_duplicate_scales(detected_scales)
    
    def _detect_key_signature(self, pitches: List[int]) -> Optional[str]:
        """Detect the overall key signature of the solo."""
        if not pitches:
            return None
        
        try:
            # Convert MIDI pitches to music21 pitches
            music21_pitches = [pitch.Pitch(p) for p in pitches]
            
            # Create a stream and analyze key
            from music21 import stream
            s = stream.Stream()
            for p in music21_pitches:
                s.append(p)
            
            # Analyze key using music21
            detected_key = s.analyze('key')
            return f"{detected_key.tonic.name} {detected_key.mode}"
            
        except Exception as e:
            logger.warning(f"Key detection failed: {e}")
            return None
    
    def _get_most_common_scales(self, detected_scales: List[ScalePattern]) -> List[Tuple[str, int]]:
        """Get the most commonly detected scales."""
        scale_counts = Counter(scale.name for scale in detected_scales)
        return scale_counts.most_common(5)
    
    def _calculate_scale_coverage(self, notes: List[Dict], detected_scales: List[ScalePattern]) -> float:
        """Calculate what percentage of notes are covered by detected scales."""
        if not notes or not detected_scales:
            return 0.0
        
        covered_notes = set()
        for scale_pattern in detected_scales:
            for note_idx in scale_pattern.notes_used:
                if note_idx < len(notes):
                    covered_notes.add(note_idx)
        
        return len(covered_notes) / len(notes) * 100.0
    
    def _remove_duplicate_scales(self, scales: List[ScalePattern]) -> List[ScalePattern]:
        """Remove duplicate or very similar scales."""
        if not scales:
            return []
        
        unique_scales = []
        for scale in scales:
            # Check if this scale is too similar to an existing one
            is_duplicate = False
            for existing in unique_scales:
                if (scale.name == existing.name and 
                    scale.root == existing.root and 
                    abs(scale.confidence - existing.confidence) < 0.1):
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_scales.append(scale)
        
        return unique_scales
    
    def export_analysis(self, analysis: ScaleAnalysis, output_path: str) -> None:
        """
        Export scale analysis results to a text file.
        
        Args:
            analysis: ScaleAnalysis object to export
            output_path: Path to save the analysis file
        """
        with open(output_path, 'w') as f:
            f.write("Jazz Scale Analysis Results\n")
            f.write("=" * 50 + "\n\n")
            
            # Write key signature
            if analysis.key_signature:
                f.write(f"Overall Key Signature: {analysis.key_signature}\n\n")
            
            # Write scale coverage
            f.write(f"Scale Coverage: {analysis.scale_coverage:.1f}% of notes\n\n")
            
            # Write most common scales
            if analysis.most_common_scales:
                f.write("Most Common Scales:\n")
                for scale_name, count in analysis.most_common_scales:
                    f.write(f"  {scale_name}: {count} occurrences\n")
                f.write("\n")
            
            # Write detailed scale detections
            f.write(f"Detected Scale Patterns ({len(analysis.detected_scales)} total):\n")
            f.write(f"{'Scale':<20} {'Root':<6} {'Confidence':<12} {'Start':<8} {'End':<8} {'Notes':<8}\n")
            f.write(f"{'-' * 70}\n")
            
            for scale_pattern in analysis.detected_scales:
                f.write(f"{scale_pattern.name:<20} {scale_pattern.root:<6} "
                       f"{scale_pattern.confidence:<12.2f} {scale_pattern.start_time:<8.2f} "
                       f"{scale_pattern.end_time:<8.2f} {len(scale_pattern.notes_used):<8}\n")
            
            # Write detailed scale information
            f.write(f"\nDetailed Scale Information:\n")
            f.write(f"{'-' * 50}\n")
            
            for i, scale_pattern in enumerate(analysis.detected_scales, 1):
                f.write(f"\n{i}. {scale_pattern.name} in {scale_pattern.root}\n")
                f.write(f"   Confidence: {scale_pattern.confidence:.2f}\n")
                f.write(f"   Time Range: {scale_pattern.start_time:.2f} - {scale_pattern.end_time:.2f}\n")
                f.write(f"   Notes Used: {len(scale_pattern.notes_used)}\n")
                f.write(f"   Pitch Classes: {scale_pattern.pitches}\n")
        
        logger.info(f"Exported scale analysis to: {output_path}")
