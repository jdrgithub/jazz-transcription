#!/usr/bin/env python3
"""
Test script for audio transcription functionality.
"""

import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from jazz_analysis.core.transcription import AudioTranscriber

def test_transcription():
    """Test the transcription system."""
    print("Testing Audio Transcription System")
    print("=" * 40)
    
    transcriber = AudioTranscriber()
    
    # Check if we have any audio files to test with
    audio_files = list(Path("audio").glob("*.wav")) + list(Path("audio").glob("*.mp3"))
    
    if not audio_files:
        print("No audio files found in audio directory.")
        print("Please add a WAV or MP3 file to the audio/ directory to test transcription.")
        return
    
    # Test with the first audio file found
    audio_file = audio_files[0]
    print(f"Testing transcription with: {audio_file}")
    
    try:
        # Transcribe the audio
        result = transcriber.transcribe_audio(str(audio_file))
        
        print(f"\nTranscription Results:")
        print(f"Duration: {result.duration:.2f} seconds")
        print(f"Tempo: {result.tempo:.1f} BPM")
        print(f"Key: {result.key or 'Unknown'}")
        print(f"Notes detected: {len(result.notes)}")
        print(f"Overall confidence: {result.confidence:.2f}")
        
        if result.notes:
            print(f"\nFirst 10 notes:")
            for i, note in enumerate(result.notes[:10]):
                print(f"  Note {i+1}: MIDI {note.pitch} ({note.start_time:.2f}s - {note.end_time:.2f}s), confidence: {note.confidence:.2f}")
        
        print("\nTranscription test completed!")
        
    except Exception as e:
        print(f"Error during transcription: {e}")
        print("This might be due to missing audio processing dependencies.")

if __name__ == "__main__":
    test_transcription()
