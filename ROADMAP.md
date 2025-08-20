# Jazz Solo Analysis Roadmap

## Core Requirements (User's Specifications)

### Primary Goal
Transcribe actual audio files and analyze jazz solos according to user specifications.

### Mandatory Features
1. **Audio Transcription Pipeline** - Transcribe audio files to notes
2. **Solo Analysis** - Detect scales, arpeggios, and approaches used
3. **Symbolic Input Support** - Load pre-transcribed solos with chord changes
4. **Archive Integration** - Use libraries of transcribed solos (Django, Bird, etc.)

### Analysis Focus (High-Level Only)
- Scale detection (harmonic minor, diminished, etc.)
- Arpeggio detection (minor-6, triads, 7ths) 
- Approach detection (chromatic enclosures, diminished bursts, etc.)
- Plain English outputs - no technical details or histograms

### User Experience
- Upload audio or load transcription
- Get analysis in plain English
- Option to correct/improve results
- Simple, direct interface

## Implementation Steps

### Phase 1: Audio Transcription
- [ ] Audio input handling (WAV, MP3)
- [ ] Source separation (isolate solo line)
- [ ] Pitch detection and note transcription
- [ ] Beat alignment and quantization
- [ ] User correction interface

### Phase 2: Analysis Engine
- [ ] Scale detection algorithms
- [ ] Arpeggio pattern recognition
- [ ] Approach tone detection
- [ ] High-level summary generation

### Phase 3: Symbolic Input
- [ ] MusicXML/MIDI/tab import
- [ ] Chord change parsing
- [ ] Same analysis engine

### Phase 4: Archive Integration
- [ ] Pre-transcribed solo libraries
- [ ] Public domain transcriptions
- [ ] Weimar Jazz Database integration

### Phase 5: User Interface
- [ ] Simple upload interface
- [ ] Analysis level selection
- [ ] Results display in plain English
- [ ] Correction/editing tools

## What NOT to Build
- Enterprise features
- Backing track generation
- Complex visualizations
- Technical internals exposed to users
- Overcomplicated architecture
