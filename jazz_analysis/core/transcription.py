"""
Audio transcription module for converting audio files to symbolic notation.
"""

import librosa
import numpy as np
from typing import List, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class Note:
    """Represents a musical note with timing and pitch information."""
    pitch: int  # MIDI pitch (0-127)
    start_time: float  # Start time in seconds
    end_time: float  # End time in seconds
    velocity: int = 100  # Note velocity (0-127)
    confidence: float = 1.0  # Transcription confidence

@dataclass
class Chord:
    """Represents a chord with timing information."""
    chord: str  # Chord name (e.g., "Cmaj7", "Dm7", "G7")
    start_time: float  # Start time in seconds
    end_time: float  # End time in seconds
    confidence: float = 1.0  # Detection confidence

@dataclass
class TranscriptionResult:
    """Result of audio transcription."""
    notes: List[Note]
    chords: List[Chord]
    tempo: float
    key: Optional[str] = None
    duration: float = 0.0
    confidence: float = 0.0

class AudioTranscriber:
    """Handles audio transcription and chord detection."""
    
    def __init__(self):
        self.sample_rate = 44100
        self.hop_length = 512
        
    def transcribe_audio(self, audio_path: str) -> TranscriptionResult:
        """
        Transcribe audio file to symbolic notation.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            TranscriptionResult with notes, chords and metadata
        """
        logger.info(f"Transcribing audio file: {audio_path}")
        
        # Load audio
        audio, sr = librosa.load(audio_path, sr=self.sample_rate)
        
        # Detect tempo
        tempo = self._detect_tempo(audio)
        
        # Extract soloist notes
        notes = self._extract_notes(audio, tempo)
        
        # Detect chord changes
        chords = self._detect_chords(audio, tempo)
        
        # Detect key
        key = self._detect_key(notes)
        
        # Calculate overall confidence
        confidence = np.mean([note.confidence for note in notes]) if notes else 0.0
        
        return TranscriptionResult(
            notes=notes,
            chords=chords,
            tempo=tempo,
            key=key,
            duration=len(audio) / self.sample_rate,
            confidence=confidence
        )
    
    def _detect_tempo(self, audio: np.ndarray) -> float:
        """Detect tempo using librosa."""
        tempo, _ = librosa.beat.beat_track(
            y=audio, 
            sr=self.sample_rate,
            hop_length=self.hop_length
        )
        return tempo
    
    def _extract_notes(self, audio: np.ndarray, tempo: float) -> List[Note]:
        """Extract soloist notes from audio using onset detection and pitch tracking."""
        notes = []
        
        # Detect onsets
        onset_frames = librosa.onset.onset_detect(
            y=audio,
            sr=self.sample_rate,
            hop_length=self.hop_length,
            units='frames'
        )
        onset_times = librosa.frames_to_time(onset_frames, sr=self.sample_rate)
        
        # Extract pitch for each onset
        for i, onset_time in enumerate(onset_times):
            # Get end time (next onset or end of audio)
            if i + 1 < len(onset_times):
                end_time = onset_times[i + 1]
            else:
                end_time = len(audio) / self.sample_rate
            
            # Extract pitch in the note region
            start_frame = int(onset_time * self.sample_rate)
            end_frame = int(end_time * self.sample_rate)
            note_audio = audio[start_frame:end_frame]
            
            if len(note_audio) > 0:
                # Use basic pitch detection
                pitch, confidence = self._detect_pitch(note_audio)
                
                if pitch > 0 and confidence > 0.5:
                    midi_pitch = int(round(12 * np.log2(pitch / 440) + 69))
                    if 21 <= midi_pitch <= 108:  # Piano range
                        notes.append(Note(
                            pitch=midi_pitch,
                            start_time=onset_time,
                            end_time=end_time,
                            confidence=confidence
                        ))
        
        return notes
    
    def _detect_chords(self, audio: np.ndarray, tempo: float) -> List[Chord]:
        """Detect chord changes from the rhythm section."""
        chords = []
        
        # Use chromagram for chord detection
        chromagram = librosa.feature.chroma_cqt(
            y=audio,
            sr=self.sample_rate,
            hop_length=self.hop_length
        )
        
        # Detect chord changes based on chromagram changes
        chord_changes = self._detect_chord_changes(chromagram)
        
        # Convert to chord names
        for i, (start_time, end_time, chord_vector) in enumerate(chord_changes):
            chord_name = self._chord_vector_to_name(chord_vector)
            chords.append(Chord(
                chord=chord_name,
                start_time=start_time,
                end_time=end_time,
                confidence=0.8  # Placeholder confidence
            ))
        
        return chords
    
    def _detect_chord_changes(self, chromagram: np.ndarray) -> List[Tuple[float, float, np.ndarray]]:
        """Detect when chord changes occur based on chromagram changes."""
        changes = []
        
        # Simple approach: detect significant changes in chromagram
        # In practice, you'd use more sophisticated chord detection
        frame_times = librosa.frames_to_time(
            np.arange(chromagram.shape[1]), 
            sr=self.sample_rate, 
            hop_length=self.hop_length
        )
        
        # For now, assume one chord per bar (4 beats)
        beat_duration = 60.0 / self._detect_tempo_from_chromagram(chromagram)
        bar_duration = beat_duration * 4
        
        for i in range(0, len(frame_times), int(bar_duration * self.sample_rate / self.hop_length)):
            if i < chromagram.shape[1]:
                start_time = frame_times[i]
                end_time = frame_times[min(i + int(bar_duration * self.sample_rate / self.hop_length), chromagram.shape[1] - 1)]
                chord_vector = np.mean(chromagram[:, i:i+int(bar_duration * self.sample_rate / self.hop_length)], axis=1)
                changes.append((start_time, end_time, chord_vector))
        
        return changes
    
    def _detect_tempo_from_chromagram(self, chromagram: np.ndarray) -> float:
        """Estimate tempo from chromagram."""
        # Simple tempo estimation
        return 120.0  # Default tempo
    
    def _chord_vector_to_name(self, chord_vector: np.ndarray) -> str:
        """Convert chromagram vector to chord name."""
        # Find the strongest pitch classes
        strongest_pcs = np.argsort(chord_vector)[-4:]  # Top 4 pitch classes
        
        # Simple chord naming (this is a basic implementation)
        # In practice, you'd use a more sophisticated chord detection algorithm
        if len(strongest_pcs) >= 3:
            # Basic major/minor detection
            root = strongest_pcs[0]
            third = strongest_pcs[1]
            
            if (third - root) % 12 == 4:  # Major third
                return f"{self._pitch_class_to_name(root)}maj"
            elif (third - root) % 12 == 3:  # Minor third
                return f"{self._pitch_class_to_name(root)}m"
        
        return "Unknown"
    
    def _pitch_class_to_name(self, pc: int) -> str:
        """Convert pitch class to note name."""
        names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        return names[pc]
    
    def _detect_pitch(self, audio: np.ndarray) -> tuple[float, float]:
        """Detect pitch using librosa."""
        pitches, magnitudes = librosa.piptrack(
            y=audio, 
            sr=self.sample_rate,
            hop_length=self.hop_length
        )
        
        if np.any(magnitudes > 0):
            max_idx = np.unravel_index(np.argmax(magnitudes), magnitudes.shape)
            pitch = pitches[max_idx]
            confidence = magnitudes[max_idx] / np.max(magnitudes)
            return pitch, confidence
        else:
            return 0.0, 0.0
    
    def _detect_key(self, notes: List[Note]) -> Optional[str]:
        """Detect key from transcribed notes."""
        if not notes:
            return None
        
        # Extract pitch classes
        pitch_classes = [note.pitch % 12 for note in notes]
        
        # Count occurrences
        from collections import Counter
        pc_counts = Counter(pitch_classes)
        
        # Simple key detection
        major_pattern = [0, 2, 4, 5, 7, 9, 11]  # C major
        minor_pattern = [0, 2, 3, 5, 7, 8, 10]  # C minor
        
        major_score = sum(pc_counts[pc] for pc in major_pattern)
        minor_score = sum(pc_counts[pc] for pc in minor_pattern)
        
        if major_score > minor_score:
            return "C"
        else:
            return "Cm"
