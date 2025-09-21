#!/usr/bin/env python3
"""
Jazz Analysis CLI - Main entry point for jazz solo analysis.
"""

import sys
import os
import sqlite3
from typing import List, Optional
from notation.data_access.weimar_jazz_client import WeimarJazzClient


class JazzAnalysisCLI:
    """Command-line interface for jazz solo analysis."""
    
    def __init__(self):
        """Initialize the CLI."""
        self.running = True
        self.weimar_client = WeimarJazzClient()
    
    def display_menu(self) -> None:
        """Display the main menu options."""
        print("\nJazz Analysis CLI")
        print("=" * 20)
        print("1. Download Weimar Jazz Database")
        print("2. Browse Available Solos")
        print("3. Select Solo for Analysis")
        print("4. Extract Solo Data")
        print("5. Exit")
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
    
    def run(self) -> None:
        """Run the main CLI loop."""
        while self.running:
            self.display_menu()
            choice = self.get_user_choice()
            self.handle_choice(choice)
        
        print("Goodbye!")


def main():
    """Main entry point."""
    cli = JazzAnalysisCLI()
    cli.run()


if __name__ == "__main__":
    main()