#!/usr/bin/env python3
"""
Main transcription script for jazz solo analysis.
"""

import sys
from pathlib import Path
import pretty_midi
import music21

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from jazz_analysis.core.transcription import AudioTranscriber

def transcribe_audio_file(audio_path: str):
    """Transcribe an audio file and create output files."""
    print(f"Transcribing: {audio_path}")
    print("=" * 50)
    
    transcriber = AudioTranscriber()
    
    try:
        result = transcriber.transcribe_audio(audio_path)
        
        # Create output directory
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        # Get base filename
        base_name = Path(audio_path).stem
        
        # Create MIDI file for solo
        midi_file = output_dir / f"{base_name}_solo.mid"
        create_midi_file(result.notes, result.tempo, midi_file)
        
        # Create chord chart text file
        chord_file = output_dir / f"{base_name}_chords.txt"
        create_chord_chart(result.chords, chord_file)
        
        # Create standard notation (MusicXML)
        notation_file = output_dir / f"{base_name}_notation.musicxml"
        create_standard_notation(result.notes, result.tempo, notation_file)
        
        print(f"Transcription completed!")
        print(f"Output files created in 'output/' directory:")
        print(f"  - {midi_file.name} (solo MIDI)")
        print(f"  - {chord_file.name} (chord chart)")
        print(f"  - {notation_file.name} (standard notation)")
        print(f"\nSummary:")
        print(f"  Duration: {result.duration:.2f} seconds")
        print(f"  Tempo: {result.tempo:.1f} BPM")
        print(f"  Soloist notes: {len(result.notes)}")
        print(f"  Chord changes: {len(result.chords)}")
        
        return result
        
    except Exception as e:
        print(f"Error during transcription: {e}")
        return None

def create_midi_file(notes, tempo, output_file):
    """Create MIDI file from transcribed notes."""
    midi = pretty_midi.PrettyMIDI(initial_tempo=tempo)
    piano_program = pretty_midi.Instrument(program=0)  # Piano
    
    for note in notes:
        note_number = note.pitch
        start_time = note.start_time
        end_time = note.end_time
        velocity = note.velocity
        
        midi_note = pretty_midi.Note(
            velocity=velocity,
            pitch=note_number,
            start=start_time,
            end=end_time
        )
        piano_program.notes.append(midi_note)
    
    midi.instruments.append(piano_program)
    midi.write(str(output_file))

def create_chord_chart(chords, output_file):
    """Create proper jazz chord chart text file."""
    with open(output_file, 'w') as f:
        f.write("Chord Chart\n")
        f.write("=" * 20 + "\n\n")
        
        # Group chords into 4-bar lines (typical jazz format)
        chords_per_line = 4
        
        for i in range(0, len(chords), chords_per_line):
            line_chords = chords[i:i+chords_per_line]
            
            # Create the chord line with | separators
            chord_line = "|"
            for chord in line_chords:
                chord_line += f" {chord.chord} |"
            
            # Pad with empty bars if needed
            while len(line_chords) < chords_per_line:
                chord_line += " |"
            
            f.write(chord_line + "\n")

def create_standard_notation(notes, tempo, output_file):
    """Create standard notation (MusicXML) from transcribed notes."""
    # Create music21 stream
    stream = music21.stream.Stream()
    stream.append(music21.tempo.MetronomeMark(number=tempo))
    
    # Group notes by time
    from collections import defaultdict
    time_notes = defaultdict(list)
    
    for note in notes:
        start_beat = int(note.start_time * tempo / 60)  # Convert to beats
        time_notes[start_beat].append(note)
    
    # Create measures
    for beat in sorted(time_notes.keys()):
        measure = music21.stream.Measure()
        
        for note in time_notes[beat]:
            # Convert MIDI pitch to music21 note
            pitch = music21.pitch.Pitch(midi=note.pitch)
            duration = note.end_time - note.start_time
            quarter_duration = duration * tempo / 60  # Convert to quarter notes
            
            music21_note = music21.note.Note(pitch)
            music21_note.duration.quarterLength = quarter_duration
            measure.append(music21_note)
        
        stream.append(measure)
    
    # Write MusicXML file
    stream.write('musicxml', fp=str(output_file))

def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) < 2:
        print("Usage: python transcribe.py <audio_file>")
        print("Example: python transcribe.py audio/solo.wav")
        return
    
    audio_file = sys.argv[1]
    
    if not Path(audio_file).exists():
        print(f"Error: Audio file '{audio_file}' not found.")
        return
    
    transcribe_audio_file(audio_file)

if __name__ == "__main__":
    main()
