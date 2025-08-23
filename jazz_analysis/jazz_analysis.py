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
        print("3. Exit")
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