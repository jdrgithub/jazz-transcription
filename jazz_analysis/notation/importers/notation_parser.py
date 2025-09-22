"""
Standard notation parser for traditional sheet music.
"""

import os
import logging
from typing import List, Dict, Optional, Tuple, Union
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    from music21 import converter, stream, note, chord, duration, pitch
    MUSIC21_AVAILABLE = True
except ImportError:
    MUSIC21_AVAILABLE = False
    logger.warning("music21 not available. Install with: pip install music21")

try:
    import fitz  # PyMuPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logger.warning("PyMuPDF not available. Install with: pip install PyMuPDF")

try:
    from PIL import Image
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    logger.warning("OCR libraries not available. Install with: pip install Pillow pytesseract")


@dataclass
class NotationData:
    """Represents parsed notation data from sheet music."""
    notes: List[Dict]  # List of note dictionaries
    chords: List[Dict]  # List of chord dictionaries
    key_signature: Optional[str] = None
    time_signature: Optional[str] = None
    tempo: Optional[int] = None
    clef: Optional[str] = None
    metadata: Dict = None


class StandardNotationParser:
    """Parser for standard musical notation from various formats."""
    
    def __init__(self):
        """Initialize the standard notation parser."""
        if not MUSIC21_AVAILABLE:
            raise ImportError("music21 is required for notation parsing. Install with: pip install music21")
        
        self.supported_formats = ['.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp']
        
        # Initialize metadata
        if self.metadata is None:
            self.metadata = {}
    
    def parse_file(self, file_path: str) -> NotationData:
        """
        Parse a standard notation file and extract musical data.
        
        Args:
            file_path: Path to the notation file
            
        Returns:
            NotationData object containing parsed musical information
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Notation file not found: {file_path}")
        
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {file_ext}. Supported formats: {self.supported_formats}")
        
        logger.info(f"Parsing notation file: {file_path}")
        
        try:
            if file_ext == '.pdf':
                return self._parse_pdf(file_path)
            elif file_ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
                return self._parse_image(file_path)
            else:
                # Try music21 for other formats
                return self._parse_with_music21(file_path)
                
        except Exception as e:
            logger.error(f"Error parsing notation file {file_path}: {e}")
            raise
    
    def _parse_pdf(self, file_path: str) -> NotationData:
        """Parse PDF notation files."""
        if not PDF_AVAILABLE:
            raise ImportError("PyMuPDF is required for PDF parsing. Install with: pip install PyMuPDF")
        
        logger.info(f"Parsing PDF file: {file_path}")
        
        # Open PDF and extract text/images
        doc = fitz.open(file_path)
        pages = []
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pages.append(page)
        
        doc.close()
        
        # For now, return basic structure - OCR implementation would go here
        return NotationData(
            notes=[],
            chords=[],
            metadata={'source': file_path, 'pages': len(pages), 'format': 'PDF'}
        )
    
    def _parse_image(self, file_path: str) -> NotationData:
        """Parse image-based notation files using OCR."""
        if not OCR_AVAILABLE:
            raise ImportError("OCR libraries required for image parsing. Install with: pip install Pillow pytesseract")
        
        logger.info(f"Parsing image file: {file_path}")
        
        # Open image
        image = Image.open(file_path)
        
        # For now, return basic structure - OCR implementation would go here
        # In a full implementation, this would use OCR to extract musical symbols
        return NotationData(
            notes=[],
            chords=[],
            metadata={'source': file_path, 'format': 'Image', 'size': image.size}
        )
    
    def _parse_with_music21(self, file_path: str) -> NotationData:
        """Parse notation files using music21."""
        logger.info(f"Parsing with music21: {file_path}")
        
        try:
            # Parse the file with music21
            score = converter.parse(file_path)
            
            # Extract musical data
            notes = self._extract_notes_from_score(score)
            chords = self._extract_chords_from_score(score)
            key_sig = self._extract_key_signature(score)
            time_sig = self._extract_time_signature(score)
            tempo = self._extract_tempo(score)
            clef = self._extract_clef(score)
            
            return NotationData(
                notes=notes,
                chords=chords,
                key_signature=key_sig,
                time_signature=time_sig,
                tempo=tempo,
                clef=clef,
                metadata={'source': file_path, 'format': 'Music21'}
            )
            
        except Exception as e:
            logger.warning(f"music21 parsing failed: {e}")
            # Return empty structure if parsing fails
            return NotationData(
                notes=[],
                chords=[],
                metadata={'source': file_path, 'format': 'Unknown', 'error': str(e)}
            )
    
    def _extract_notes_from_score(self, score: stream.Score) -> List[Dict]:
        """Extract note data from a music21 score."""
        notes = []
        
        for part in score.parts:
            for element in part.flat.notes:
                if isinstance(element, note.Note):
                    note_data = {
                        'onset': float(element.offset),
                        'pitch': element.pitch.midi,
                        'duration': float(element.duration.quarterLength),
                        'step': element.pitch.step,
                        'octave': element.pitch.octave,
                        'accidental': element.pitch.accidental.name if element.pitch.accidental else None
                    }
                    notes.append(note_data)
        
        return notes
    
    def _extract_chords_from_score(self, score: stream.Score) -> List[Dict]:
        """Extract chord data from a music21 score."""
        chords = []
        
        for part in score.parts:
            for element in part.flat.notes:
                if isinstance(element, chord.Chord):
                    chord_data = {
                        'onset': float(element.offset),
                        'pitches': [p.midi for p in element.pitches],
                        'duration': float(element.duration.quarterLength),
                        'root': element.root().name if hasattr(element, 'root') else None,
                        'quality': element.quality if hasattr(element, 'quality') else None
                    }
                    chords.append(chord_data)
        
        return chords
    
    def _extract_key_signature(self, score: stream.Score) -> Optional[str]:
        """Extract key signature from score."""
        for part in score.parts:
            for element in part.flat:
                if hasattr(element, 'sharps') and hasattr(element, 'mode'):
                    return f"{element.sharps} {element.mode}"
        return None
    
    def _extract_time_signature(self, score: stream.Score) -> Optional[str]:
        """Extract time signature from score."""
        for part in score.parts:
            for element in part.flat:
                if hasattr(element, 'numerator') and hasattr(element, 'denominator'):
                    return f"{element.numerator}/{element.denominator}"
        return None
    
    def _extract_tempo(self, score: stream.Score) -> Optional[int]:
        """Extract tempo from score."""
        for part in score.parts:
            for element in part.flat:
                if hasattr(element, 'number'):
                    return int(element.number)
        return None
    
    def _extract_clef(self, score: stream.Score) -> Optional[str]:
        """Extract clef information from score."""
        for part in score.parts:
            for element in part.flat:
                if hasattr(element, 'sign'):
                    return element.sign
        return None
    
    def export_to_text(self, notation_data: NotationData, output_path: str) -> None:
        """
        Export parsed notation data to a text file.
        
        Args:
            notation_data: Parsed notation data
            output_path: Path to save the text file
        """
        with open(output_path, 'w') as f:
            f.write("Standard Notation Parsed Data\n")
            f.write("=" * 50 + "\n\n")
            
            # Write metadata
            f.write("Metadata:\n")
            for key, value in notation_data.metadata.items():
                f.write(f"  {key}: {value}\n")
            f.write("\n")
            
            # Write musical information
            if notation_data.key_signature:
                f.write(f"Key Signature: {notation_data.key_signature}\n")
            if notation_data.time_signature:
                f.write(f"Time Signature: {notation_data.time_signature}\n")
            if notation_data.tempo:
                f.write(f"Tempo: {notation_data.tempo} BPM\n")
            if notation_data.clef:
                f.write(f"Clef: {notation_data.clef}\n")
            f.write("\n")
            
            # Write notes
            f.write(f"Notes ({len(notation_data.notes)} total):\n")
            if notation_data.notes:
                f.write(f"{'Onset':<10} {'Pitch':<8} {'Duration':<10} {'Step':<6} {'Octave':<8} {'Accidental':<10}\n")
                f.write(f"{'-' * 60}\n")
                
                for note_data in notation_data.notes:
                    f.write(f"{note_data['onset']:<10.3f} {note_data['pitch']:<8} {note_data['duration']:<10.3f} "
                           f"{note_data['step']:<6} {note_data['octave']:<8} {note_data['accidental'] or 'None':<10}\n")
            else:
                f.write("No notes found.\n")
            f.write("\n")
            
            # Write chords
            f.write(f"Chords ({len(notation_data.chords)} total):\n")
            if notation_data.chords:
                f.write(f"{'Onset':<10} {'Duration':<10} {'Root':<8} {'Quality':<10} {'Pitches':<20}\n")
                f.write(f"{'-' * 60}\n")
                
                for chord_data in notation_data.chords:
                    pitches_str = ','.join(map(str, chord_data['pitches']))
                    f.write(f"{chord_data['onset']:<10.3f} {chord_data['duration']:<10.3f} "
                           f"{chord_data['root'] or 'N/A':<8} {chord_data['quality'] or 'N/A':<10} {pitches_str:<20}\n")
            else:
                f.write("No chords found.\n")
        
        logger.info(f"Exported notation data to: {output_path}")
