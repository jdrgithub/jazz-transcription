"""
Core analysis engine for jazz solo transcription and analysis.
"""

from .transcription import AudioTranscriber, Note, TranscriptionResult

__all__ = [
    'AudioTranscriber',
    'Note', 
    'TranscriptionResult'
]
