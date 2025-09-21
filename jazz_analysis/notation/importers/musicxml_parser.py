"""
MusicXML parser for importing jazz solo notation.
"""

import os
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

try:
    from music21 import converter, stream, note, chord, duration, pitch
    MUSIC21_AVAILABLE = True
except ImportError:
    MUSIC21_AVAILABLE = False
    logger.warning("music21 not available. Install with: pip install music21")


@dataclass
class NoteData:
    """Represents a single note in the solo."""
    onset: float  # Start time in beats
    pitch: int    # MIDI pitch number
    duration: float  # Duration in beats
    velocity: int    # MIDI velocity (0-127)
    octave: int      # Octave number
    step: str        # Note name (C, D, E, F, G, A, B)
    accidental: Optional[str] = None  # Sharp, flat, natural


@dataclass
class ChordData:
    """Represents a chord in the solo."""
    onset: float
    pitches: List[int]  # List of MIDI pitch numbers
    duration: float
    root: Optional[str] = None  # Chord root note
    quality: Optional[str] = None  # Major, minor, dominant, etc.


class MusicXMLParser:
    """Parser for MusicXML files from Weimar Jazz Database."""
    
    def __init__(self):
        """Initialize the MusicXML parser."""
        if not MUSIC21_AVAILABLE:
            raise ImportError("music21 is required for MusicXML parsing. Install with: pip install music21")
    
    def parse_file(self, file_path: str) -> Tuple[List[NoteData], List[ChordData]]:
        """
        Parse a MusicXML file and extract notes and chords.
        
        Args:
            file_path: Path to the MusicXML file
            
        Returns:
            Tuple of (notes, chords) extracted from the file
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"MusicXML file not found: {file_path}")
        
        logger.info(f"Parsing MusicXML file: {file_path}")
        
        try:
            # Parse the MusicXML file
            score = converter.parse(file_path)
            
            # Extract notes and chords
            notes = self._extract_notes(score)
            chords = self._extract_chords(score)
            
            logger.info(f"Extracted {len(notes)} notes and {len(chords)} chords")
            return notes, chords
            
        except Exception as e:
            logger.error(f"Error parsing MusicXML file {file_path}: {e}")
            raise
    
    def _extract_notes(self, score: stream.Score) -> List[NoteData]:
        """Extract note data from the parsed score."""
        notes = []
        
        # Get all parts in the score
        for part in score.parts:
            # Get all notes in the part
            for element in part.flat.notes:
                if isinstance(element, note.Note):
                    note_data = self._convert_note(element)
                    if note_data:
                        notes.append(note_data)
                elif isinstance(element, chord.Chord):
                    # Convert chord to individual notes
                    for n in element.notes:
                        note_data = self._convert_note(n, element.offset, element.duration.quarterLength)
                        if note_data:
                            notes.append(note_data)
        
        # Sort notes by onset time
        notes.sort(key=lambda n: n.onset)
        return notes
    
    def _extract_chords(self, score: stream.Score) -> List[ChordData]:
        """Extract chord data from the parsed score."""
        chords = []
        
        # Get all parts in the score
        for part in score.parts:
            # Get all chords in the part
            for element in part.flat.notes:
                if isinstance(element, chord.Chord):
                    chord_data = self._convert_chord(element)
                    if chord_data:
                        chords.append(chord_data)
        
        # Sort chords by onset time
        chords.sort(key=lambda c: c.onset)
        return chords
    
    def _convert_note(self, note_obj: note.Note, offset: float = None, duration: float = None) -> Optional[NoteData]:
        """Convert a music21 Note object to our NoteData format."""
        try:
            # Get pitch information
            pitch_obj = note_obj.pitch
            midi_pitch = pitch_obj.midi
            
            # Get timing information
            note_onset = offset if offset is not None else note_obj.offset
            note_duration = duration if duration is not None else note_obj.duration.quarterLength
            
            # Get velocity (default to 80 if not specified)
            velocity = getattr(note_obj, 'volume', None)
            if velocity is not None:
                velocity = int(velocity.velocityScalar * 127)
            else:
                velocity = 80  # Default velocity
            
            return NoteData(
                onset=float(note_onset),
                pitch=midi_pitch,
                duration=float(note_duration),
                velocity=velocity,
                octave=pitch_obj.octave,
                step=pitch_obj.step,
                accidental=pitch_obj.accidental.name if pitch_obj.accidental else None
            )
            
        except Exception as e:
            logger.warning(f"Error converting note: {e}")
            return None
    
    def _convert_chord(self, chord_obj: chord.Chord) -> Optional[ChordData]:
        """Convert a music21 Chord object to our ChordData format."""
        try:
            # Get pitch information
            pitches = [p.midi for p in chord_obj.pitches]
            
            # Get timing information
            chord_onset = chord_obj.offset
            chord_duration = chord_obj.duration.quarterLength
            
            # Try to get chord root and quality
            root = None
            quality = None
            try:
                chord_symbol = chord_obj.figure
                if chord_symbol:
                    # Parse chord symbol (e.g., "C", "Cm", "C7")
                    root = chord_symbol[0] if chord_symbol else None
                    quality = chord_symbol[1:] if len(chord_symbol) > 1 else "major"
            except:
                pass
            
            return ChordData(
                onset=float(chord_onset),
                pitches=pitches,
                duration=float(chord_duration),
                root=root,
                quality=quality
            )
            
        except Exception as e:
            logger.warning(f"Error converting chord: {e}")
            return None
    
    def export_to_text(self, notes: List[NoteData], chords: List[ChordData], output_path: str) -> None:
        """
        Export parsed data to a text file for analysis.
        
        Args:
            notes: List of extracted notes
            chords: List of extracted chords
            output_path: Path to save the text file
        """
        with open(output_path, 'w') as f:
            f.write("MusicXML Parsed Data\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"Notes ({len(notes)} total):\n")
            f.write(f"{'Onset':<10} {'Pitch':<8} {'Duration':<10} {'Velocity':<8} {'Note':<8}\n")
            f.write(f"{'-' * 50}\n")
            
            for note_data in notes:
                note_name = f"{note_data.step}{note_data.accidental or ''}{note_data.octave}"
                f.write(f"{note_data.onset:<10.3f} {note_data.pitch:<8} {note_data.duration:<10.3f} {note_data.velocity:<8} {note_name:<8}\n")
            
            f.write(f"\nChords ({len(chords)} total):\n")
            f.write(f"{'Onset':<10} {'Duration':<10} {'Root':<8} {'Quality':<10} {'Pitches':<20}\n")
            f.write(f"{'-' * 60}\n")
            
            for chord_data in chords:
                pitches_str = ','.join(map(str, chord_data.pitches))
                f.write(f"{chord_data.onset:<10.3f} {chord_data.duration:<10.3f} {chord_data.root or 'N/A':<8} {chord_data.quality or 'N/A':<10} {pitches_str:<20}\n")
        
        logger.info(f"Exported parsed data to: {output_path}")
