#!/usr/bin/env python3
"""
Jazz Analysis CLI - Main entry point for jazz solo analysis.
"""

import sys
import os
import sqlite3
from typing import List, Optional, Tuple
from notation.data_access.weimar_jazz_client import WeimarJazzClient
from notation.importers.musicxml_parser import MusicXMLParser
from notation.importers.notation_parser import StandardNotationParser
from notation.analysis.scale_detector import JazzScaleDetector
from notation.analysis.arpeggio_detector import JazzArpeggioDetector
from notation.analysis.approach_detector import JazzApproachDetector
from notation.analysis.summary_generator import JazzAnalysisSummaryGenerator
from notation.analysis.text_formatter import JazzAnalysisTextFormatter
from notation.database.local_solo_database import LocalSoloDatabase, SoloRecord
from notation.data_access.public_domain_client import PublicDomainClient, PublicDomainTranscription


class JazzAnalysisCLI:
    """Command-line interface for jazz solo analysis."""
    
    def __init__(self):
        """Initialize the CLI."""
        self.running = True
        self.weimar_client = WeimarJazzClient()
        self.musicxml_parser = MusicXMLParser()
        self.notation_parser = StandardNotationParser()
        self.scale_detector = JazzScaleDetector()
        self.arpeggio_detector = JazzArpeggioDetector()
        self.approach_detector = JazzApproachDetector()
        self.summary_generator = JazzAnalysisSummaryGenerator()
        self.text_formatter = JazzAnalysisTextFormatter()
        self.local_database = LocalSoloDatabase()
        self.public_domain_client = PublicDomainClient()
    
    def display_menu(self) -> None:
        """Display the main menu options."""
        print("\nJazz Analysis CLI")
        print("=" * 20)
        print("1. Download Weimar Jazz Database")
        print("2. Browse Available Solos")
        print("3. Select Solo for Analysis")
        print("4. Extract Solo Data")
        print("5. Import MusicXML File")
        print("6. Import Standard Notation")
        print("7. Analyze Jazz Scales")
        print("8. Analyze Jazz Arpeggios")
        print("9. Analyze Approach Tones")
        print("10. Generate Analysis Summary")
        print("11. Generate Formatted Report")
        print("12. Manage Local Solo Library")
        print("13. Public Domain Transcriptions")
        print("14. Exit")
        print()
    
    def get_user_choice(self) -> str:
        """Get user input for menu selection."""
        return input("Enter your choice: ").strip()
    
    def handle_choice(self, choice: str) -> None:
        """Handle user menu choice."""
        if choice == "1":
            self.download_weimar_database()
        elif choice == "2":
            self.browse_solos()
        elif choice == "3":
            self.select_solo()
        elif choice == "4":
            self.extract_solo_data()
        elif choice == "5":
            self.import_musicxml_file()
        elif choice == "6":
            self.import_standard_notation()
        elif choice == "7":
            self.analyze_jazz_scales()
        elif choice == "8":
            self.analyze_jazz_arpeggios()
        elif choice == "9":
            self.analyze_approach_tones()
        elif choice == "10":
            self.generate_analysis_summary()
        elif choice == "11":
            self.generate_formatted_report()
        elif choice == "12":
            self.manage_local_solo_library()
        elif choice == "13":
            self.manage_public_domain_transcriptions()
        elif choice == "14":
            self.running = False
        else:
            print("Invalid choice. Please try again.")
    
    def download_weimar_database(self) -> None:
        """Download the Weimar Jazz Database."""
        print("Downloading Weimar Jazz Database...")
        
        # Create data directory if it doesn't exist
        data_dir = "data"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        output_path = os.path.join(data_dir, "weimar_jazz_database.db")
        
        if self.weimar_client.download_database(output_path):
            print(f"Successfully downloaded database to {output_path}")
        else:
            print("Failed to download database. Please check your internet connection.")
    
    def browse_solos(self) -> None:
        """Browse available solos in the Weimar database."""
        db_path = "data/weimar_jazz_database.db"
        
        if not os.path.exists(db_path):
            print("Database not found. Please download it first (option 1).")
            return
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get basic database info
            cursor.execute("SELECT COUNT(*) FROM melody")
            total_solos = cursor.fetchone()[0]
            
            print(f"\nWeimar Jazz Database contains {total_solos} solos.")
            
            # Get sample of solos with metadata
            cursor.execute("""
                SELECT si.melid, si.title, si.performer, si.key, si.avgtempo
                FROM solo_info si
                LIMIT 10
            """)
            
            solos = cursor.fetchall()
            print("\nSample of available solos:")
            print("-" * 50)
            
            for solo in solos:
                melid, title, performer, key, tempo = solo
                print(f"ID: {melid} | {title} by {performer} | Key: {key} | Tempo: {tempo}")
            
            conn.close()
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        except Exception as e:
            print(f"Error browsing solos: {e}")
    
    def select_solo(self) -> None:
        """Select a specific solo for analysis."""
        db_path = "data/weimar_jazz_database.db"
        
        if not os.path.exists(db_path):
            print("Database not found. Please download it first (option 1).")
            return
        
        try:
            # Get user input for solo ID
            solo_id = input("Enter solo ID to select: ").strip()
            
            if not solo_id.isdigit():
                print("Please enter a valid numeric ID.")
                return
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get detailed solo information
            cursor.execute("""
                SELECT si.melid, si.title, si.performer, si.key, si.avgtempo, 
                       si.instrument, si.style, si.chord_changes
                FROM solo_info si
                WHERE si.melid = ?
            """, (solo_id,))
            
            solo = cursor.fetchone()
            
            if solo:
                melid, title, performer, key, tempo, instrument, style, chord_changes = solo
                print(f"\nSelected Solo:")
                print(f"ID: {melid}")
                print(f"Title: {title}")
                print(f"Performer: {performer}")
                print(f"Key: {key}")
                print(f"Tempo: {tempo}")
                print(f"Instrument: {instrument}")
                print(f"Style: {style}")
                print(f"Chord Changes:")
                formatted_changes = self.format_chord_changes(chord_changes)
                print(formatted_changes)
                print(f"\nSolo selected for analysis!")
            else:
                print(f"No solo found with ID {solo_id}")
            
            conn.close()
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        except Exception as e:
            print(f"Error selecting solo: {e}")
    
    def format_chord_changes(self, chord_changes: str) -> str:
        """Format chord changes to display 4 bars per line with proper alignment."""
        if not chord_changes:
            return "No chord changes available"
        
        # Split by bars (||) and clean up
        bars = chord_changes.replace('||', '|').split('|')
        bars = [bar.strip() for bar in bars if bar.strip()]
        
        # Process bars and handle section labels
        formatted_lines = []
        current_line = []
        
        for bar in bars:
            # Check if this is a section label (A1:, B1:, etc.)
            if ':' in bar and any(section in bar for section in ['A1:', 'A2:', 'A3:', 'B1:', 'B2:']):
                # If we have bars in current line, add them
                if current_line:
                    # Pad each bar to consistent width for alignment
                    padded_bars = [bar.ljust(8) for bar in current_line]
                    line = ' | '.join(padded_bars)
                    formatted_lines.append(f"| {line} |")
                    current_line = []
                # Add section label on its own line
                formatted_lines.append(f"{bar}")
            else:
                current_line.append(bar)
                # If we have 4 bars, add the line
                if len(current_line) == 4:
                    # Pad each bar to consistent width for alignment
                    padded_bars = [bar.ljust(8) for bar in current_line]
                    line = ' | '.join(padded_bars)
                    formatted_lines.append(f"| {line} |")
                    current_line = []
        
        # Add any remaining bars
        if current_line:
            # Pad each bar to consistent width for alignment
            padded_bars = [bar.ljust(8) for bar in current_line]
            line = ' | '.join(padded_bars)
            formatted_lines.append(f"| {line} |")
        
        return '\n'.join(formatted_lines)
    
    def extract_solo_data(self) -> None:
        """Extract solo notes and timing data for analysis."""
        db_path = "data/weimar_jazz_database.db"
        
        if not os.path.exists(db_path):
            print("Database not found. Please download it first (option 1).")
            return
        
        try:
            # Get solo ID from user
            solo_id = input("Enter solo ID to extract data: ").strip()
            if not solo_id:
                print("No solo ID provided.")
                return
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get solo metadata
            cursor.execute("""
                SELECT si.melid, si.title, si.performer, si.key, si.avgtempo, 
                       si.instrument, si.style, si.chordchanges
                FROM solo_info si
                WHERE si.melid = ?
            """, (solo_id,))
            
            solo_info = cursor.fetchone()
            if not solo_info:
                print(f"Solo with ID {solo_id} not found.")
                conn.close()
                return
            
            melid, title, performer, key, tempo, instrument, style, chord_changes = solo_info
            
            print(f"\nExtracting data for: {title} by {performer}")
            print(f"Key: {key}, Tempo: {tempo}, Instrument: {instrument}, Style: {style}")
            
            # Get melody notes data
            cursor.execute("""
                SELECT onset, pitch, duration, velocity
                FROM melody
                WHERE melid = ?
                ORDER BY onset
            """, (solo_id,))
            
            notes = cursor.fetchall()
            if not notes:
                print("No melody data found for this solo.")
                conn.close()
                return
            
            print(f"Found {len(notes)} notes in the solo.")
            
            # Create output directory
            output_dir = "extracted_data"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Generate output filename
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_performer = "".join(c for c in performer if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{solo_id}_{safe_performer}_{safe_title}.txt"
            output_path = os.path.join(output_dir, filename)
            
            # Write extracted data to file
            with open(output_path, 'w') as f:
                f.write(f"Jazz Solo Analysis Data\n")
                f.write(f"=" * 50 + "\n\n")
                f.write(f"Title: {title}\n")
                f.write(f"Performer: {performer}\n")
                f.write(f"Key: {key}\n")
                f.write(f"Tempo: {tempo} BPM\n")
                f.write(f"Instrument: {instrument}\n")
                f.write(f"Style: {style}\n")
                f.write(f"Solo ID: {melid}\n\n")
                
                f.write(f"Chord Changes:\n")
                f.write(f"{self.format_chord_changes(chord_changes)}\n\n")
                
                f.write(f"Melody Notes ({len(notes)} total):\n")
                f.write(f"{'Onset':<10} {'Pitch':<8} {'Duration':<10} {'Velocity':<8}\n")
                f.write(f"{'-' * 40}\n")
                
                for onset, pitch, duration, velocity in notes:
                    f.write(f"{onset:<10.3f} {pitch:<8} {duration:<10.3f} {velocity:<8}\n")
            
            print(f"Successfully extracted solo data to: {output_path}")
            print(f"Data includes {len(notes)} notes with timing and pitch information.")
            
            conn.close()
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        except Exception as e:
            print(f"Error extracting solo data: {e}")
    
    def import_musicxml_file(self) -> None:
        """Import and parse a MusicXML file."""
        file_path = input("Enter path to MusicXML file: ").strip()
        
        if not file_path:
            print("No file path provided.")
            return
        
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return
        
        if not file_path.lower().endswith(('.xml', '.musicxml')):
            print("File must be a MusicXML file (.xml or .musicxml)")
            return
        
        try:
            print(f"Parsing MusicXML file: {file_path}")
            
            # Parse the MusicXML file
            notes, chords = self.musicxml_parser.parse_file(file_path)
            
            print(f"Successfully parsed {len(notes)} notes and {len(chords)} chords")
            
            # Create output directory
            output_dir = "parsed_musicxml"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Generate output filename
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            output_path = os.path.join(output_dir, f"{base_name}_parsed.txt")
            
            # Export parsed data
            self.musicxml_parser.export_to_text(notes, chords, output_path)
            
            print(f"Parsed data exported to: {output_path}")
            
        except ImportError as e:
            print(f"Error: {e}")
            print("Please install music21: pip install music21")
        except Exception as e:
            print(f"Error parsing MusicXML file: {e}")
    
    def import_standard_notation(self) -> None:
        """Import and parse standard notation files."""
        file_path = input("Enter path to notation file (PDF, PNG, JPG, etc.): ").strip()
        
        if not file_path:
            print("No file path provided.")
            return
        
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return
        
        # Check file extension
        supported_extensions = ['.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp']
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext not in supported_extensions:
            print(f"Unsupported file format: {file_ext}")
            print(f"Supported formats: {', '.join(supported_extensions)}")
            return
        
        try:
            print(f"Parsing notation file: {file_path}")
            
            # Parse the notation file
            notation_data = self.notation_parser.parse_file(file_path)
            
            print(f"Successfully parsed notation data:")
            print(f"  - Notes: {len(notation_data.notes)}")
            print(f"  - Chords: {len(notation_data.chords)}")
            if notation_data.key_signature:
                print(f"  - Key: {notation_data.key_signature}")
            if notation_data.time_signature:
                print(f"  - Time: {notation_data.time_signature}")
            if notation_data.tempo:
                print(f"  - Tempo: {notation_data.tempo} BPM")
            
            # Create output directory
            output_dir = "parsed_notation"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Generate output filename
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            output_path = os.path.join(output_dir, f"{base_name}_parsed.txt")
            
            # Export parsed data
            self.notation_parser.export_to_text(notation_data, output_path)
            
            print(f"Parsed data exported to: {output_path}")
            
        except ImportError as e:
            print(f"Error: {e}")
            print("Please install required dependencies:")
            print("  - For PDF: pip install PyMuPDF")
            print("  - For images: pip install Pillow pytesseract")
        except Exception as e:
            print(f"Error parsing notation file: {e}")
    
    def analyze_jazz_scales(self) -> None:
        """Analyze jazz scales in extracted or imported solo data."""
        print("\nJazz Scale Analysis")
        print("=" * 20)
        print("1. Analyze extracted Weimar solo data")
        print("2. Analyze imported MusicXML data")
        print("3. Analyze imported notation data")
        print("4. Back to main menu")
        
        choice = input("Enter your choice: ").strip()
        
        if choice == "1":
            self._analyze_weimar_data()
        elif choice == "2":
            self._analyze_musicxml_data()
        elif choice == "3":
            self._analyze_notation_data()
        elif choice == "4":
            return
        else:
            print("Invalid choice.")
    
    def _analyze_weimar_data(self) -> None:
        """Analyze scales in Weimar database solo data."""
        solo_id = input("Enter solo ID to analyze: ").strip()
        
        if not solo_id:
            print("No solo ID provided.")
            return
        
        db_path = "data/weimar_jazz_database.db"
        if not os.path.exists(db_path):
            print("Database not found. Please download it first (option 1).")
            return
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get melody notes data
            cursor.execute("""
                SELECT onset, pitch, duration, velocity
                FROM melody
                WHERE melid = ?
                ORDER BY onset
            """, (solo_id,))
            
            notes_data = cursor.fetchall()
            if not notes_data:
                print("No melody data found for this solo.")
                conn.close()
                return
            
            # Convert to our format
            notes = []
            for onset, pitch, duration, velocity in notes_data:
                notes.append({
                    'onset': onset,
                    'pitch': pitch,
                    'duration': duration,
                    'velocity': velocity
                })
            
            print(f"Analyzing {len(notes)} notes for jazz scales...")
            
            # Perform scale analysis
            analysis = self.scale_detector.analyze_notes(notes)
            
            # Display results
            self._display_scale_analysis(analysis)
            
            # Export results
            output_dir = "scale_analysis"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            output_path = os.path.join(output_dir, f"solo_{solo_id}_scale_analysis.txt")
            self.scale_detector.export_analysis(analysis, output_path)
            print(f"Analysis exported to: {output_path}")
            
            conn.close()
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        except Exception as e:
            print(f"Error analyzing scales: {e}")
    
    def _analyze_musicxml_data(self) -> None:
        """Analyze scales in imported MusicXML data."""
        print("MusicXML scale analysis not yet implemented.")
        print("Please use the Weimar database analysis for now.")
    
    def _analyze_notation_data(self) -> None:
        """Analyze scales in imported notation data."""
        print("Notation scale analysis not yet implemented.")
        print("Please use the Weimar database analysis for now.")
    
    def _display_scale_analysis(self, analysis) -> None:
        """Display scale analysis results."""
        print(f"\nScale Analysis Results:")
        print(f"=" * 30)
        
        if analysis.key_signature:
            print(f"Overall Key: {analysis.key_signature}")
        
        print(f"Scale Coverage: {analysis.scale_coverage:.1f}% of notes")
        
        if analysis.most_common_scales:
            print(f"\nMost Common Scales:")
            for scale_name, count in analysis.most_common_scales:
                print(f"  {scale_name}: {count} occurrences")
        
        print(f"\nDetected Scale Patterns ({len(analysis.detected_scales)} total):")
        print(f"{'Scale':<20} {'Root':<6} {'Confidence':<12} {'Time Range':<15}")
        print(f"{'-' * 60}")
        
        for scale_pattern in analysis.detected_scales[:10]:  # Show top 10
            time_range = f"{scale_pattern.start_time:.1f}-{scale_pattern.end_time:.1f}"
            print(f"{scale_pattern.name:<20} {scale_pattern.root:<6} "
                  f"{scale_pattern.confidence:<12.2f} {time_range:<15}")
    
    def analyze_jazz_arpeggios(self) -> None:
        """Analyze jazz arpeggios in extracted or imported solo data."""
        print("\nJazz Arpeggio Analysis")
        print("=" * 20)
        print("1. Analyze extracted Weimar solo data")
        print("2. Analyze imported MusicXML data")
        print("3. Analyze imported notation data")
        print("4. Back to main menu")
        
        choice = input("Enter your choice: ").strip()
        
        if choice == "1":
            self._analyze_weimar_arpeggios()
        elif choice == "2":
            self._analyze_musicxml_arpeggios()
        elif choice == "3":
            self._analyze_notation_arpeggios()
        elif choice == "4":
            return
        else:
            print("Invalid choice.")
    
    def _analyze_weimar_arpeggios(self) -> None:
        """Analyze arpeggios in Weimar database solo data."""
        solo_id = input("Enter solo ID to analyze: ").strip()
        
        if not solo_id:
            print("No solo ID provided.")
            return
        
        db_path = "data/weimar_jazz_database.db"
        if not os.path.exists(db_path):
            print("Database not found. Please download it first (option 1).")
            return
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get melody notes data
            cursor.execute("""
                SELECT onset, pitch, duration, velocity
                FROM melody
                WHERE melid = ?
                ORDER BY onset
            """, (solo_id,))
            
            notes_data = cursor.fetchall()
            if not notes_data:
                print("No melody data found for this solo.")
                conn.close()
                return
            
            # Convert to our format
            notes = []
            for onset, pitch, duration, velocity in notes_data:
                notes.append({
                    'onset': onset,
                    'pitch': pitch,
                    'duration': duration,
                    'velocity': velocity
                })
            
            print(f"Analyzing {len(notes)} notes for jazz arpeggios...")
            
            # Perform arpeggio analysis
            analysis = self.arpeggio_detector.analyze_notes(notes)
            
            # Display results
            self._display_arpeggio_analysis(analysis)
            
            # Export results
            output_dir = "arpeggio_analysis"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            output_path = os.path.join(output_dir, f"solo_{solo_id}_arpeggio_analysis.txt")
            self.arpeggio_detector.export_analysis(analysis, output_path)
            print(f"Analysis exported to: {output_path}")
            
            conn.close()
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        except Exception as e:
            print(f"Error analyzing arpeggios: {e}")
    
    def _analyze_musicxml_arpeggios(self) -> None:
        """Analyze arpeggios in imported MusicXML data."""
        print("MusicXML arpeggio analysis not yet implemented.")
        print("Please use the Weimar database analysis for now.")
    
    def _analyze_notation_arpeggios(self) -> None:
        """Analyze arpeggios in imported notation data."""
        print("Notation arpeggio analysis not yet implemented.")
        print("Please use the Weimar database analysis for now.")
    
    def _display_arpeggio_analysis(self, analysis) -> None:
        """Display arpeggio analysis results."""
        print(f"\nArpeggio Analysis Results:")
        print(f"=" * 30)
        
        print(f"Arpeggio Coverage: {analysis.arpeggio_coverage:.1f}% of notes")
        
        if analysis.most_common_arpeggios:
            print(f"\nMost Common Arpeggios:")
            for arpeggio_name, count in analysis.most_common_arpeggios:
                print(f"  {arpeggio_name}: {count} occurrences")
        
        if analysis.chord_progression:
            print(f"\nChord Progression:")
            for chord_name, time in analysis.chord_progression[:10]:  # Show first 10
                print(f"  {time:.2f}: {chord_name}")
        
        print(f"\nDetected Arpeggio Patterns ({len(analysis.detected_arpeggios)} total):")
        print(f"{'Arpeggio':<25} {'Direction':<12} {'Confidence':<12} {'Time Range':<15}")
        print(f"{'-' * 70}")
        
        for arpeggio in analysis.detected_arpeggios[:10]:  # Show top 10
            time_range = f"{arpeggio.start_time:.1f}-{arpeggio.end_time:.1f}"
            print(f"{arpeggio.name:<25} {arpeggio.direction:<12} "
                  f"{arpeggio.confidence:<12.2f} {time_range:<15}")
    
    def analyze_approach_tones(self) -> None:
        """Analyze approach tones in extracted or imported solo data."""
        print("\nJazz Approach Tone Analysis")
        print("=" * 20)
        print("1. Analyze extracted Weimar solo data")
        print("2. Analyze imported MusicXML data")
        print("3. Analyze imported notation data")
        print("4. Back to main menu")
        
        choice = input("Enter your choice: ").strip()
        
        if choice == "1":
            self._analyze_weimar_approach_tones()
        elif choice == "2":
            self._analyze_musicxml_approach_tones()
        elif choice == "3":
            self._analyze_notation_approach_tones()
        elif choice == "4":
            return
        else:
            print("Invalid choice.")
    
    def _analyze_weimar_approach_tones(self) -> None:
        """Analyze approach tones in Weimar database solo data."""
        solo_id = input("Enter solo ID to analyze: ").strip()
        
        if not solo_id:
            print("No solo ID provided.")
            return
        
        db_path = "data/weimar_jazz_database.db"
        if not os.path.exists(db_path):
            print("Database not found. Please download it first (option 1).")
            return
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get melody notes data
            cursor.execute("""
                SELECT onset, pitch, duration, velocity
                FROM melody
                WHERE melid = ?
                ORDER BY onset
            """, (solo_id,))
            
            notes_data = cursor.fetchall()
            if not notes_data:
                print("No melody data found for this solo.")
                conn.close()
                return
            
            # Convert to our format
            notes = []
            for onset, pitch, duration, velocity in notes_data:
                notes.append({
                    'onset': onset,
                    'pitch': pitch,
                    'duration': duration,
                    'velocity': velocity
                })
            
            print(f"Analyzing {len(notes)} notes for jazz approach tones...")
            
            # Get chord progression for context (if available)
            cursor.execute("""
                SELECT chordchanges
                FROM solo_info
                WHERE melid = ?
            """, (solo_id,))
            
            chord_result = cursor.fetchone()
            chord_progression = None
            if chord_result and chord_result[0]:
                # Parse chord changes for context
                chord_progression = self._parse_chord_changes(chord_result[0])
            
            # Perform approach tone analysis
            analysis = self.approach_detector.analyze_notes(notes, chord_progression)
            
            # Display results
            self._display_approach_analysis(analysis)
            
            # Export results
            output_dir = "approach_analysis"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            output_path = os.path.join(output_dir, f"solo_{solo_id}_approach_analysis.txt")
            self.approach_detector.export_analysis(analysis, output_path)
            print(f"Analysis exported to: {output_path}")
            
            conn.close()
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        except Exception as e:
            print(f"Error analyzing approach tones: {e}")
    
    def _parse_chord_changes(self, chord_changes: str) -> List[Tuple[str, float]]:
        """Parse chord changes string into chord progression."""
        # Simplified chord progression parsing
        # In a full implementation, this would parse the chord changes more accurately
        
        if not chord_changes:
            return []
        
        # Split by bars and create basic chord progression
        bars = chord_changes.replace('||', '|').split('|')
        bars = [bar.strip() for bar in bars if bar.strip()]
        
        chord_progression = []
        current_time = 0.0
        
        for bar in bars:
            # Skip section labels
            if ':' in bar and any(section in bar for section in ['A1:', 'A2:', 'A3:', 'B1:', 'B2:']):
                continue
            
            # Split bar into chords (simplified)
            chords = [chord.strip() for chord in bar.split() if chord.strip()]
            
            for chord in chords:
                chord_progression.append((chord, current_time))
                current_time += 1.0  # Assume 1 beat per chord
        
        return chord_progression
    
    def _analyze_musicxml_approach_tones(self) -> None:
        """Analyze approach tones in imported MusicXML data."""
        print("MusicXML approach tone analysis not yet implemented.")
        print("Please use the Weimar database analysis for now.")
    
    def _analyze_notation_approach_tones(self) -> None:
        """Analyze approach tones in imported notation data."""
        print("Notation approach tone analysis not yet implemented.")
        print("Please use the Weimar database analysis for now.")
    
    def _display_approach_analysis(self, analysis) -> None:
        """Display approach tone analysis results."""
        print(f"\nApproach Tone Analysis Results:")
        print(f"=" * 30)
        
        print(f"Approach Coverage: {analysis.approach_coverage:.1f}% of notes")
        
        if analysis.most_common_patterns:
            print(f"\nMost Common Approach Patterns:")
            for pattern_name, count in analysis.most_common_patterns:
                print(f"  {pattern_name}: {count} occurrences")
        
        if analysis.target_notes:
            print(f"\nMost Targeted Notes:")
            for target_pitch, frequency in analysis.target_notes[:5]:  # Show top 5
                from music21 import pitch
                note_name = pitch.Pitch(target_pitch).name
                print(f"  {note_name}: {frequency} times")
        
        print(f"\nDetected Approach Patterns ({len(analysis.detected_patterns)} total):")
        print(f"{'Pattern':<25} {'Type':<12} {'Direction':<10} {'Confidence':<12} {'Time Range':<15}")
        print(f"{'-' * 80}")
        
        for pattern in analysis.detected_patterns[:10]:  # Show top 10
            time_range = f"{pattern.start_time:.1f}-{pattern.end_time:.1f}"
            print(f"{pattern.name:<25} {pattern.pattern_type:<12} {pattern.direction:<10} "
                  f"{pattern.confidence:<12.2f} {time_range:<15}")
    
    def run(self) -> None:
        """Run the main CLI loop."""
        while self.running:
            self.display_menu()
            choice = self.get_user_choice()
            self.handle_choice(choice)
        
        print("Goodbye!")
    
    def generate_analysis_summary(self) -> None:
        """Generate comprehensive analysis summary from all analysis results."""
        print("\nAnalysis Summary Generator")
        print("=" * 30)
        print("1. Generate summary from Weimar solo data")
        print("2. Generate summary from MusicXML data")
        print("3. Generate summary from notation data")
        print("4. Back to main menu")
        
        choice = input("Enter your choice: ").strip()
        
        if choice == "1":
            self._generate_weimar_summary()
        elif choice == "2":
            self._generate_musicxml_summary()
        elif choice == "3":
            self._generate_notation_summary()
        elif choice == "4":
            return
        else:
            print("Invalid choice.")
    
    def _generate_weimar_summary(self) -> None:
        """Generate analysis summary from Weimar database solo data."""
        solo_id = input("Enter solo ID to analyze: ").strip()
        
        if not solo_id:
            print("No solo ID provided.")
            return
        
        db_path = "data/weimar_jazz_database.db"
        if not os.path.exists(db_path):
            print("Database not found. Please download it first (option 1).")
            return
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get solo metadata
            cursor.execute("""
                SELECT si.title, si.performer, si.key, si.avgtempo, si.chordchanges
                FROM solo_info si
                WHERE si.melid = ?
            """, (solo_id,))
            
            solo_info = cursor.fetchone()
            if not solo_info:
                print("Solo not found in database.")
                conn.close()
                return
            
            title, performer, key, tempo, chord_changes = solo_info
            
            # Get melody notes data
            cursor.execute("""
                SELECT onset, pitch, duration, velocity
                FROM melody
                WHERE melid = ?
                ORDER BY onset
            """, (solo_id,))
            
            notes_data = cursor.fetchall()
            if not notes_data:
                print("No melody data found for this solo.")
                conn.close()
                return
            
            # Convert to our format
            notes = []
            for onset, pitch, duration, velocity in notes_data:
                notes.append({
                    'onset': onset,
                    'pitch': pitch,
                    'duration': duration,
                    'velocity': velocity
                })
            
            print(f"Generating comprehensive analysis for {len(notes)} notes...")
            
            # Perform all analyses
            print("Analyzing scales...")
            scale_analysis = self.scale_detector.analyze_notes(notes)
            
            print("Analyzing arpeggios...")
            chord_progression = self._parse_chord_changes(chord_changes) if chord_changes else None
            arpeggio_analysis = self.arpeggio_detector.analyze_notes(notes, chord_progression)
            
            print("Analyzing approach tones...")
            approach_analysis = self.approach_detector.analyze_notes(notes, chord_progression)
            
            # Prepare metadata
            solo_metadata = {
                'title': title or 'Unknown Solo',
                'performer': performer or 'Unknown Performer',
                'key': key or 'Unknown Key',
                'tempo': tempo,
                'total_notes': len(notes)
            }
            
            # Generate comprehensive summary
            print("Generating analysis summary...")
            summary = self.summary_generator.generate_summary(
                scale_analysis, arpeggio_analysis, approach_analysis, solo_metadata
            )
            
            # Display summary
            self._display_analysis_summary(summary)
            
            # Export summary
            output_dir = "analysis_summaries"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            output_path = os.path.join(output_dir, f"solo_{solo_id}_summary.txt")
            self.summary_generator.export_summary(summary, output_path)
            print(f"Analysis summary exported to: {output_path}")
            
            conn.close()
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        except Exception as e:
            print(f"Error generating analysis summary: {e}")
    
    def _generate_musicxml_summary(self) -> None:
        """Generate analysis summary from MusicXML data."""
        print("MusicXML summary generation not yet implemented.")
        print("This feature will be available in a future update.")
    
    def _generate_notation_summary(self) -> None:
        """Generate analysis summary from notation data."""
        print("Notation summary generation not yet implemented.")
        print("This feature will be available in a future update.")
    
    def _display_analysis_summary(self, summary) -> None:
        """Display analysis summary results."""
        print(f"\nANALYSIS SUMMARY")
        print(f"=" * 50)
        print(f"Solo: {summary.solo_title}")
        print(f"Performer: {summary.performer}")
        print(f"Key: {summary.key_signature}")
        if summary.tempo:
            print(f"Tempo: {summary.tempo} BPM")
        print(f"Total Notes: {summary.total_notes}")
        
        print(f"\nOVERALL ASSESSMENT")
        print(f"-" * 20)
        print(f"Character: {summary.overall_character}")
        print(f"Technical Level: {summary.technical_level}")
        print(f"Harmonic Sophistication: {summary.harmonic_sophistication}")
        
        print(f"\nANALYSIS COVERAGE")
        print(f"-" * 18)
        for analysis_type, coverage in summary.analysis_coverage.items():
            print(f"{analysis_type.replace('_', ' ').title()}: {coverage:.1f}%")
        
        print(f"\nKEY INSIGHTS")
        print(f"-" * 12)
        if summary.scale_insights:
            print("Scale Analysis:")
            for insight in summary.scale_insights:
                print(f"  • {insight}")
        
        if summary.arpeggio_insights:
            print("\nArpeggio Analysis:")
            for insight in summary.arpeggio_insights:
                print(f"  • {insight}")
        
        if summary.approach_insights:
            print("\nApproach Tone Analysis:")
            for insight in summary.approach_insights:
                print(f"  • {insight}")
        
        if summary.recommendations:
            print(f"\nSTUDY RECOMMENDATIONS")
            print(f"-" * 21)
            for recommendation in summary.recommendations:
                print(f"• {recommendation}")
    
    def generate_formatted_report(self) -> None:
        """Generate formatted analysis report with chord changes and analysis by bar."""
        print("\nFormatted Report Generator")
        print("=" * 30)
        print("1. Generate formatted report from Weimar solo data")
        print("2. Generate formatted report from MusicXML data")
        print("3. Generate formatted report from notation data")
        print("4. Back to main menu")
        
        choice = input("Enter your choice: ").strip()
        
        if choice == "1":
            self._generate_weimar_formatted_report()
        elif choice == "2":
            self._generate_musicxml_formatted_report()
        elif choice == "3":
            self._generate_notation_formatted_report()
        elif choice == "4":
            return
        else:
            print("Invalid choice.")
    
    def _generate_weimar_formatted_report(self) -> None:
        """Generate formatted report from Weimar database solo data."""
        solo_id = input("Enter solo ID to analyze: ").strip()
        
        if not solo_id:
            print("No solo ID provided.")
            return
        
        db_path = "data/weimar_jazz_database.db"
        if not os.path.exists(db_path):
            print("Database not found. Please download it first (option 1).")
            return
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get solo metadata
            cursor.execute("""
                SELECT si.title, si.performer, si.key, si.avgtempo, si.chordchanges
                FROM solo_info si
                WHERE si.melid = ?
            """, (solo_id,))
            
            solo_info = cursor.fetchone()
            if not solo_info:
                print("Solo not found in database.")
                conn.close()
                return
            
            title, performer, key, tempo, chord_changes = solo_info
            
            # Get melody notes data
            cursor.execute("""
                SELECT onset, pitch, duration, velocity
                FROM melody
                WHERE melid = ?
                ORDER BY onset
            """, (solo_id,))
            
            notes_data = cursor.fetchall()
            if not notes_data:
                print("No melody data found for this solo.")
                conn.close()
                return
            
            # Convert to our format
            notes = []
            for onset, pitch, duration, velocity in notes_data:
                notes.append({
                    'onset': onset,
                    'pitch': pitch,
                    'duration': duration,
                    'velocity': velocity
                })
            
            print(f"Generating formatted report for {len(notes)} notes...")
            
            # Perform all analyses
            print("Analyzing scales...")
            scale_analysis = self.scale_detector.analyze_notes(notes)
            
            print("Analyzing arpeggios...")
            chord_progression = self._parse_chord_changes(chord_changes) if chord_changes else None
            arpeggio_analysis = self.arpeggio_detector.analyze_notes(notes, chord_progression)
            
            print("Analyzing approach tones...")
            approach_analysis = self.approach_detector.analyze_notes(notes, chord_progression)
            
            # Generate analysis summary
            print("Generating analysis summary...")
            solo_metadata = {
                'title': title or 'Unknown Solo',
                'performer': performer or 'Unknown Performer',
                'key': key or 'Unknown Key',
                'tempo': tempo,
                'total_notes': len(notes)
            }
            
            analysis_summary = self.summary_generator.generate_summary(
                scale_analysis, arpeggio_analysis, approach_analysis, solo_metadata
            )
            
            # Format the report
            print("Formatting analysis report...")
            formatted_analysis = self.text_formatter.format_analysis_report(
                analysis_summary, scale_analysis, arpeggio_analysis, approach_analysis,
                chord_changes or "", solo_metadata
            )
            
            # Display the formatted report
            self.text_formatter.display_formatted_report(formatted_analysis)
            
            # Export the formatted report
            output_dir = "formatted_reports"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            output_path = os.path.join(output_dir, f"solo_{solo_id}_formatted_report.txt")
            self.text_formatter.export_formatted_report(formatted_analysis, output_path)
            print(f"Formatted report exported to: {output_path}")
            
            conn.close()
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        except Exception as e:
            print(f"Error generating formatted report: {e}")
    
    def _generate_musicxml_formatted_report(self) -> None:
        """Generate formatted report from MusicXML data."""
        print("MusicXML formatted report generation not yet implemented.")
        print("This feature will be available in a future update.")
    
    def _generate_notation_formatted_report(self) -> None:
        """Generate formatted report from notation data."""
        print("Notation formatted report generation not yet implemented.")
        print("This feature will be available in a future update.")
    
    def manage_local_solo_library(self) -> None:
        """Manage the local solo library database."""
        print("\nLocal Solo Library Management")
        print("=" * 35)
        print("1. View all stored solos")
        print("2. Search solos by criteria")
        print("3. View solo details")
        print("4. Save analyzed solo to library")
        print("5. Delete solo from library")
        print("6. View library statistics")
        print("7. Export library data")
        print("8. Import library data")
        print("9. Back to main menu")
        
        choice = input("Enter your choice: ").strip()
        
        if choice == "1":
            self._view_all_solos()
        elif choice == "2":
            self._search_solos()
        elif choice == "3":
            self._view_solo_details()
        elif choice == "4":
            self._save_solo_to_library()
        elif choice == "5":
            self._delete_solo_from_library()
        elif choice == "6":
            self._view_library_statistics()
        elif choice == "7":
            self._export_library_data()
        elif choice == "8":
            self._import_library_data()
        elif choice == "9":
            return
        else:
            print("Invalid choice.")
    
    def _view_all_solos(self) -> None:
        """View all solos in the local library."""
        solos = self.local_database.get_all_solos()
        
        if not solos:
            print("No solos found in the local library.")
            return
        
        print(f"\nLocal Solo Library ({len(solos)} solos)")
        print("=" * 50)
        print(f"{'ID':<4} {'Title':<25} {'Performer':<20} {'Source':<8} {'Level':<12}")
        print("-" * 70)
        
        for solo in solos:
            print(f"{solo.id:<4} {solo.title[:24]:<25} {solo.performer[:19]:<20} "
                  f"{solo.source_type:<8} {solo.technical_level:<12}")
    
    def _search_solos(self) -> None:
        """Search solos by various criteria."""
        print("\nSearch Solos")
        print("-" * 15)
        
        performer = input("Performer (optional, partial match): ").strip() or None
        source_type = input("Source type (weimar/musicxml/notation, optional): ").strip() or None
        technical_level = input("Technical level (optional): ").strip() or None
        harmonic_sophistication = input("Harmonic sophistication (optional): ").strip() or None
        
        solos = self.local_database.search_solos(
            performer=performer,
            source_type=source_type,
            technical_level=technical_level,
            harmonic_sophistication=harmonic_sophistication
        )
        
        if not solos:
            print("No solos found matching the criteria.")
            return
        
        print(f"\nSearch Results ({len(solos)} solos)")
        print("=" * 40)
        print(f"{'ID':<4} {'Title':<25} {'Performer':<20} {'Source':<8} {'Level':<12}")
        print("-" * 70)
        
        for solo in solos:
            print(f"{solo.id:<4} {solo.title[:24]:<25} {solo.performer[:19]:<20} "
                  f"{solo.source_type:<8} {solo.technical_level:<12}")
    
    def _view_solo_details(self) -> None:
        """View detailed information about a specific solo."""
        solo_id = input("Enter solo ID: ").strip()
        
        if not solo_id.isdigit():
            print("Invalid solo ID.")
            return
        
        solo = self.local_database.get_solo(int(solo_id))
        if not solo:
            print("Solo not found.")
            return
        
        print(f"\nSolo Details - ID: {solo.id}")
        print("=" * 40)
        print(f"Title: {solo.title}")
        print(f"Performer: {solo.performer}")
        print(f"Key: {solo.key_signature}")
        if solo.tempo:
            print(f"Tempo: {solo.tempo} BPM")
        print(f"Source: {solo.source_type} (ID: {solo.source_id})")
        print(f"Total Notes: {solo.total_notes}")
        print(f"Analysis Date: {solo.analysis_date}")
        print(f"Technical Level: {solo.technical_level}")
        print(f"Harmonic Sophistication: {solo.harmonic_sophistication}")
        print(f"Overall Character: {solo.overall_character}")
        print(f"Analysis Coverage:")
        print(f"  Scales: {solo.scale_coverage:.1f}%")
        print(f"  Arpeggios: {solo.arpeggio_coverage:.1f}%")
        print(f"  Approach Tones: {solo.approach_coverage:.1f}%")
        
        if solo.formatted_report_path and os.path.exists(solo.formatted_report_path):
            print(f"Formatted Report: {solo.formatted_report_path}")
        else:
            print("Formatted Report: Not available")
    
    def _save_solo_to_library(self) -> None:
        """Save a recently analyzed solo to the local library."""
        print("\nSave Solo to Library")
        print("-" * 22)
        print("This feature will save a solo that was recently analyzed.")
        print("You need to provide the solo ID from a recent analysis.")
        
        # For now, this is a placeholder - in a full implementation,
        # this would integrate with the analysis workflow to save results
        print("This feature requires integration with the analysis workflow.")
        print("It will be implemented in a future update.")
    
    def _delete_solo_from_library(self) -> None:
        """Delete a solo from the local library."""
        solo_id = input("Enter solo ID to delete: ").strip()
        
        if not solo_id.isdigit():
            print("Invalid solo ID.")
            return
        
        solo = self.local_database.get_solo(int(solo_id))
        if not solo:
            print("Solo not found.")
            return
        
        print(f"Are you sure you want to delete '{solo.title}' by {solo.performer}? (y/N)")
        confirm = input().strip().lower()
        
        if confirm == 'y':
            if self.local_database.delete_solo(int(solo_id)):
                print("Solo deleted successfully.")
            else:
                print("Failed to delete solo.")
        else:
            print("Deletion cancelled.")
    
    def _view_library_statistics(self) -> None:
        """View library statistics."""
        stats = self.local_database.get_statistics()
        
        print(f"\nLocal Solo Library Statistics")
        print("=" * 35)
        print(f"Total Solos: {stats['total_solos']}")
        
        if stats['by_source_type']:
            print(f"\nBy Source Type:")
            for source_type, count in stats['by_source_type'].items():
                print(f"  {source_type}: {count}")
        
        if stats['by_technical_level']:
            print(f"\nBy Technical Level:")
            for level, count in stats['by_technical_level'].items():
                print(f"  {level}: {count}")
        
        if stats['by_harmonic_sophistication']:
            print(f"\nBy Harmonic Sophistication:")
            for sophistication, count in stats['by_harmonic_sophistication'].items():
                print(f"  {sophistication}: {count}")
        
        avg_coverage = stats['average_coverage']
        print(f"\nAverage Analysis Coverage:")
        print(f"  Scales: {avg_coverage['scale']:.1f}%")
        print(f"  Arpeggios: {avg_coverage['arpeggio']:.1f}%")
        print(f"  Approach Tones: {avg_coverage['approach']:.1f}%")
    
    def _export_library_data(self) -> None:
        """Export library data to a JSON file."""
        output_path = input("Enter output file path (e.g., library_export.json): ").strip()
        
        if not output_path:
            print("No output path provided.")
            return
        
        try:
            self.local_database.export_solo_data(output_path)
            print(f"Library data exported to: {output_path}")
        except Exception as e:
            print(f"Error exporting library data: {e}")
    
    def _import_library_data(self) -> None:
        """Import library data from a JSON file."""
        input_path = input("Enter input file path: ").strip()
        
        if not input_path or not os.path.exists(input_path):
            print("Invalid input file path.")
            return
        
        try:
            imported_count = self.local_database.import_solo_data(input_path)
            print(f"Successfully imported {imported_count} solos.")
        except Exception as e:
            print(f"Error importing library data: {e}")
    
    def manage_public_domain_transcriptions(self) -> None:
        """Manage public domain jazz transcriptions."""
        print("\nPublic Domain Transcriptions")
        print("=" * 35)
        print("1. Search public domain transcriptions")
        print("2. View downloaded transcriptions")
        print("3. Download transcription")
        print("4. Delete downloaded transcription")
        print("5. View available sources")
        print("6. View cache statistics")
        print("7. Analyze downloaded transcription")
        print("8. Back to main menu")
        
        choice = input("Enter your choice: ").strip()
        
        if choice == "1":
            self._search_public_domain_transcriptions()
        elif choice == "2":
            self._view_downloaded_transcriptions()
        elif choice == "3":
            self._download_transcription()
        elif choice == "4":
            self._delete_downloaded_transcription()
        elif choice == "5":
            self._view_available_sources()
        elif choice == "6":
            self._view_cache_statistics()
        elif choice == "7":
            self._analyze_downloaded_transcription()
        elif choice == "8":
            return
        else:
            print("Invalid choice.")
    
    def _search_public_domain_transcriptions(self) -> None:
        """Search for public domain transcriptions."""
        print("\nSearch Public Domain Transcriptions")
        print("-" * 35)
        
        query = input("Enter search query (e.g., 'jazz', 'bebop', 'charlie parker'): ").strip()
        if not query:
            print("No search query provided.")
            return
        
        source = input("Source (imslp/mutopia/cpdl, optional): ").strip() or None
        genre = input("Genre (optional): ").strip() or None
        difficulty = input("Difficulty (Beginner/Intermediate/Advanced/Expert, optional): ").strip() or None
        
        try:
            print(f"Searching for '{query}'...")
            transcriptions = self.public_domain_client.search_transcriptions(
                query=query,
                source=source,
                genre=genre,
                difficulty=difficulty,
                limit=10
            )
            
            if not transcriptions:
                print("No transcriptions found matching your criteria.")
                return
            
            print(f"\nSearch Results ({len(transcriptions)} found)")
            print("=" * 50)
            print(f"{'ID':<12} {'Title':<25} {'Performer':<20} {'Source':<8} {'Format':<8} {'Difficulty':<10}")
            print("-" * 85)
            
            for transcription in transcriptions:
                print(f"{transcription.id:<12} {transcription.title[:24]:<25} "
                      f"{transcription.performer[:19]:<20} {transcription.source:<8} "
                      f"{transcription.file_format:<8} {transcription.difficulty_level:<10}")
            
            print(f"\nUse option 3 to download any of these transcriptions.")
            
        except Exception as e:
            print(f"Error searching transcriptions: {e}")
    
    def _view_downloaded_transcriptions(self) -> None:
        """View downloaded transcriptions."""
        transcriptions = self.public_domain_client.get_downloaded_transcriptions()
        
        if not transcriptions:
            print("No downloaded transcriptions found.")
            return
        
        print(f"\nDownloaded Transcriptions ({len(transcriptions)} total)")
        print("=" * 60)
        print(f"{'ID':<12} {'Title':<25} {'Performer':<20} {'Source':<8} {'Format':<8} {'Downloaded':<12}")
        print("-" * 90)
        
        for transcription in transcriptions:
            download_date = transcription.download_date.split('T')[0]  # Just the date part
            print(f"{transcription.id:<12} {transcription.title[:24]:<25} "
                  f"{transcription.performer[:19]:<20} {transcription.source:<8} "
                  f"{transcription.file_format:<8} {download_date:<12}")
    
    def _download_transcription(self) -> None:
        """Download a transcription."""
        transcription_id = input("Enter transcription ID to download: ").strip()
        
        if not transcription_id:
            print("No transcription ID provided.")
            return
        
        # First search for the transcription
        try:
            transcriptions = self.public_domain_client.search_transcriptions("", limit=50)
            transcription = None
            
            for t in transcriptions:
                if t.id == transcription_id:
                    transcription = t
                    break
            
            if not transcription:
                print("Transcription not found.")
                return
            
            print(f"Downloading: {transcription.title} by {transcription.performer}")
            print(f"Source: {transcription.source}")
            print(f"Format: {transcription.file_format}")
            
            if self.public_domain_client.download_transcription(transcription):
                print("Transcription downloaded successfully!")
                print(f"File saved to: {transcription.file_path}")
            else:
                print("Failed to download transcription.")
                
        except Exception as e:
            print(f"Error downloading transcription: {e}")
    
    def _delete_downloaded_transcription(self) -> None:
        """Delete a downloaded transcription."""
        transcription_id = input("Enter transcription ID to delete: ").strip()
        
        if not transcription_id:
            print("No transcription ID provided.")
            return
        
        transcription = self.public_domain_client.get_transcription_by_id(transcription_id)
        if not transcription:
            print("Transcription not found.")
            return
        
        print(f"Are you sure you want to delete '{transcription.title}' by {transcription.performer}? (y/N)")
        confirm = input().strip().lower()
        
        if confirm == 'y':
            if self.public_domain_client.delete_transcription(transcription_id):
                print("Transcription deleted successfully.")
            else:
                print("Failed to delete transcription.")
        else:
            print("Deletion cancelled.")
    
    def _view_available_sources(self) -> None:
        """View available public domain sources."""
        sources = self.public_domain_client.get_available_sources()
        
        print(f"\nAvailable Public Domain Sources")
        print("=" * 40)
        
        for source_id, source_info in sources.items():
            print(f"\n{source_info['name']} ({source_id})")
            print(f"  URL: {source_info['base_url']}")
            print(f"  Description: {source_info['description']}")
    
    def _view_cache_statistics(self) -> None:
        """View cache statistics."""
        stats = self.public_domain_client.get_cache_statistics()
        
        print(f"\nPublic Domain Cache Statistics")
        print("=" * 35)
        print(f"Total Transcriptions: {stats['total_transcriptions']}")
        print(f"Total Cache Size: {stats['total_size_mb']} MB")
        
        if stats['by_source']:
            print(f"\nBy Source:")
            for source, count in stats['by_source'].items():
                print(f"  {source}: {count}")
        
        if stats['by_format']:
            print(f"\nBy Format:")
            for file_format, count in stats['by_format'].items():
                print(f"  {file_format}: {count}")
        
        if stats['by_difficulty']:
            print(f"\nBy Difficulty:")
            for difficulty, count in stats['by_difficulty'].items():
                print(f"  {difficulty}: {count}")
    
    def _analyze_downloaded_transcription(self) -> None:
        """Analyze a downloaded transcription."""
        transcription_id = input("Enter transcription ID to analyze: ").strip()
        
        if not transcription_id:
            print("No transcription ID provided.")
            return
        
        transcription = self.public_domain_client.get_transcription_by_id(transcription_id)
        if not transcription:
            print("Transcription not found.")
            return
        
        if not transcription.file_path or not os.path.exists(transcription.file_path):
            print("Transcription file not found.")
            return
        
        print(f"Analyzing: {transcription.title} by {transcription.performer}")
        print(f"File: {transcription.file_path}")
        
        # For now, this is a placeholder - in a full implementation,
        # this would integrate with the analysis workflow
        print("This feature requires integration with the analysis workflow.")
        print("It will be implemented in a future update.")
        print("For now, you can manually import the file using the MusicXML or notation import options.")


def main():
    """Main entry point."""
    cli = JazzAnalysisCLI()
    cli.run()


if __name__ == "__main__":
    main()