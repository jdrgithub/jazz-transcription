#!/usr/bin/env python3
"""
Jazz Analysis CLI - Main entry point for jazz solo analysis.
"""

import sys
from typing import List, Optional


class JazzAnalysisCLI:
    """Command-line interface for jazz solo analysis."""
    
    def __init__(self):
        """Initialize the CLI."""
        self.running = True
    
    def display_menu(self) -> None:
        """Display the main menu options."""
        print("\nJazz Analysis CLI")
        print("=" * 20)
        print("1. Download Weimar Jazz Database")
        print("2. Exit")
        print()
    
    def get_user_choice(self) -> str:
        """Get user input for menu selection."""
        return input("Enter your choice: ").strip()
    
    def handle_choice(self, choice: str) -> None:
        """Handle user menu choice."""
        if choice == "1":
            print("Weimar Jazz Database download option selected.")
            # TODO: Implement download functionality
        elif choice == "2":
            self.running = False
        else:
            print("Invalid choice. Please try again.")
    
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