"""
Text Output Formatter for Jazz Solo Analysis.

This module formats analysis results into readable text reports with chord changes,
analysis findings, and musical insights in a structured format.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
import os
from datetime import datetime


@dataclass
class FormattedAnalysis:
    """Container for formatted analysis output."""
    title: str
    performer: str
    key_signature: str
    tempo: Optional[float]
    chord_changes: List[str]
    analysis_by_bar: Dict[int, Dict[str, Any]]
    overall_summary: str
    technical_notes: List[str]
    study_recommendations: List[str]


class JazzAnalysisTextFormatter:
    """Formats jazz analysis results into readable text reports."""
    
    def __init__(self):
        """Initialize the text formatter."""
        self.bars_per_line = 4
        self.chord_padding = 12
        self.section_markers = ['A1:', 'A2:', 'A3:', 'B1:', 'B2:', 'C1:', 'C2:', 'Bridge:', 'Intro:', 'Outro:']
    
    def format_analysis_report(self, 
                             analysis_summary: Any,
                             scale_analysis: Any,
                             arpeggio_analysis: Any,
                             approach_analysis: Any,
                             chord_changes: str,
                             solo_metadata: Dict[str, Any]) -> FormattedAnalysis:
        """Format comprehensive analysis into a structured text report."""
        
        # Extract basic metadata
        title = solo_metadata.get('title', 'Unknown Solo')
        performer = solo_metadata.get('performer', 'Unknown Performer')
        key_signature = solo_metadata.get('key', 'Unknown Key')
        tempo = solo_metadata.get('tempo')
        
        # Parse and format chord changes
        formatted_chord_changes = self._format_chord_changes(chord_changes)
        
        # Create analysis by bar mapping
        analysis_by_bar = self._create_analysis_by_bar(
            scale_analysis, arpeggio_analysis, approach_analysis
        )
        
        # Generate overall summary
        overall_summary = self._generate_overall_summary(analysis_summary)
        
        # Extract technical notes
        technical_notes = self._extract_technical_notes(
            scale_analysis, arpeggio_analysis, approach_analysis
        )
        
        # Extract study recommendations
        study_recommendations = self._extract_study_recommendations(analysis_summary)
        
        return FormattedAnalysis(
            title=title,
            performer=performer,
            key_signature=key_signature,
            tempo=tempo,
            chord_changes=formatted_chord_changes,
            analysis_by_bar=analysis_by_bar,
            overall_summary=overall_summary,
            technical_notes=technical_notes,
            study_recommendations=study_recommendations
        )
    
    def _format_chord_changes(self, chord_changes: str) -> List[str]:
        """Format chord changes into readable lines with proper alignment."""
        if not chord_changes:
            return ["No chord changes available"]
        
        # Split by bars and handle section labels
        bars = chord_changes.replace('||', '|').split('|')
        bars = [bar.strip() for bar in bars if bar.strip()]
        
        formatted_lines = []
        current_line = ""
        bar_count = 0
        
        for bar in bars:
            # Handle section labels
            if any(marker in bar for marker in self.section_markers):
                if current_line:
                    formatted_lines.append(current_line.rstrip())
                    current_line = ""
                    bar_count = 0
                formatted_lines.append(f"\n{bar}")
                continue
            
            # Add chord to current line
            if current_line:
                current_line += " | "
            current_line += bar.ljust(self.chord_padding)
            bar_count += 1
            
            # Start new line after 4 bars
            if bar_count >= self.bars_per_line:
                formatted_lines.append(current_line.rstrip())
                current_line = ""
                bar_count = 0
        
        # Add remaining bars
        if current_line:
            formatted_lines.append(current_line.rstrip())
        
        return formatted_lines
    
    def _create_analysis_by_bar(self, 
                               scale_analysis: Any,
                               arpeggio_analysis: Any,
                               approach_analysis: Any) -> Dict[int, Dict[str, Any]]:
        """Create analysis mapping by bar number."""
        analysis_by_bar = {}
        
        # Process scale analysis by bar
        if hasattr(scale_analysis, 'detected_scales') and scale_analysis.detected_scales:
            for scale in scale_analysis.detected_scales:
                bar_num = int(scale.start_time) + 1  # Convert to 1-based bar numbering
                if bar_num not in analysis_by_bar:
                    analysis_by_bar[bar_num] = {'scales': [], 'arpeggios': [], 'approach_tones': []}
                analysis_by_bar[bar_num]['scales'].append({
                    'type': scale.scale_type,
                    'confidence': scale.confidence,
                    'time_range': f"{scale.start_time:.1f}-{scale.end_time:.1f}"
                })
        
        # Process arpeggio analysis by bar
        if hasattr(arpeggio_analysis, 'detected_arpeggios') and arpeggio_analysis.detected_arpeggios:
            for arpeggio in arpeggio_analysis.detected_arpeggios:
                bar_num = int(arpeggio.start_time) + 1
                if bar_num not in analysis_by_bar:
                    analysis_by_bar[bar_num] = {'scales': [], 'arpeggios': [], 'approach_tones': []}
                analysis_by_bar[bar_num]['arpeggios'].append({
                    'type': arpeggio.arpeggio_type,
                    'direction': arpeggio.direction,
                    'confidence': arpeggio.confidence,
                    'time_range': f"{arpeggio.start_time:.1f}-{arpeggio.end_time:.1f}"
                })
        
        # Process approach tone analysis by bar
        if hasattr(approach_analysis, 'detected_patterns') and approach_analysis.detected_patterns:
            for pattern in approach_analysis.detected_patterns:
                bar_num = int(pattern.start_time) + 1
                if bar_num not in analysis_by_bar:
                    analysis_by_bar[bar_num] = {'scales': [], 'arpeggios': [], 'approach_tones': []}
                analysis_by_bar[bar_num]['approach_tones'].append({
                    'type': pattern.pattern_type,
                    'target_note': pattern.target_note,
                    'confidence': pattern.confidence,
                    'time_range': f"{pattern.start_time:.1f}-{pattern.end_time:.1f}"
                })
        
        return analysis_by_bar
    
    def _generate_overall_summary(self, analysis_summary: Any) -> str:
        """Generate overall summary text."""
        if not analysis_summary:
            return "No analysis summary available."
        
        summary_parts = []
        
        if hasattr(analysis_summary, 'overall_character'):
            summary_parts.append(f"Overall Character: {analysis_summary.overall_character}")
        
        if hasattr(analysis_summary, 'technical_level'):
            summary_parts.append(f"Technical Level: {analysis_summary.technical_level}")
        
        if hasattr(analysis_summary, 'harmonic_sophistication'):
            summary_parts.append(f"Harmonic Sophistication: {analysis_summary.harmonic_sophistication}")
        
        if hasattr(analysis_summary, 'analysis_coverage'):
            coverage_text = []
            for analysis_type, coverage in analysis_summary.analysis_coverage.items():
                coverage_text.append(f"{analysis_type.replace('_', ' ').title()}: {coverage:.1f}%")
            summary_parts.append(f"Analysis Coverage: {', '.join(coverage_text)}")
        
        return "\n".join(summary_parts)
    
    def _extract_technical_notes(self, 
                                scale_analysis: Any,
                                arpeggio_analysis: Any,
                                approach_analysis: Any) -> List[str]:
        """Extract technical notes from analysis results."""
        notes = []
        
        # Scale analysis notes
        if hasattr(scale_analysis, 'detected_scales') and scale_analysis.detected_scales:
            scale_types = {}
            for scale in scale_analysis.detected_scales:
                scale_type = scale.scale_type
                scale_types[scale_type] = scale_types.get(scale_type, 0) + 1
            
            if scale_types:
                most_common = max(scale_types.items(), key=lambda x: x[1])
                notes.append(f"Most prominent scale: {most_common[0]} ({most_common[1]} occurrences)")
        
        # Arpeggio analysis notes
        if hasattr(arpeggio_analysis, 'detected_arpeggios') and arpeggio_analysis.detected_arpeggios:
            arpeggio_types = {}
            for arpeggio in arpeggio_analysis.detected_arpeggios:
                arpeggio_type = arpeggio.arpeggio_type
                arpeggio_types[arpeggio_type] = arpeggio_types.get(arpeggio_type, 0) + 1
            
            if arpeggio_types:
                most_common = max(arpeggio_types.items(), key=lambda x: x[1])
                notes.append(f"Most prominent arpeggio: {most_common[0]} ({most_common[1]} occurrences)")
        
        # Approach tone analysis notes
        if hasattr(approach_analysis, 'detected_patterns') and approach_analysis.detected_patterns:
            pattern_types = {}
            for pattern in approach_analysis.detected_patterns:
                pattern_type = pattern.pattern_type
                pattern_types[pattern_type] = pattern_types.get(pattern_type, 0) + 1
            
            if pattern_types:
                most_common = max(pattern_types.items(), key=lambda x: x[1])
                notes.append(f"Most prominent approach pattern: {most_common[0]} ({most_common[1]} occurrences)")
        
        return notes
    
    def _extract_study_recommendations(self, analysis_summary: Any) -> List[str]:
        """Extract study recommendations from analysis summary."""
        if hasattr(analysis_summary, 'recommendations'):
            return analysis_summary.recommendations
        return []
    
    def export_formatted_report(self, formatted_analysis: FormattedAnalysis, output_path: str) -> None:
        """Export formatted analysis report to a text file."""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                # Header
                f.write("JAZZ SOLO ANALYSIS REPORT\n")
                f.write("=" * 50 + "\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Basic information
                f.write("SOLO INFORMATION\n")
                f.write("-" * 18 + "\n")
                f.write(f"Title: {formatted_analysis.title}\n")
                f.write(f"Performer: {formatted_analysis.performer}\n")
                f.write(f"Key: {formatted_analysis.key_signature}\n")
                if formatted_analysis.tempo:
                    f.write(f"Tempo: {formatted_analysis.tempo} BPM\n")
                f.write("\n")
                
                # Chord changes
                f.write("CHORD CHANGES\n")
                f.write("-" * 13 + "\n")
                for line in formatted_analysis.chord_changes:
                    f.write(f"{line}\n")
                f.write("\n")
                
                # Overall summary
                f.write("OVERALL ANALYSIS SUMMARY\n")
                f.write("-" * 26 + "\n")
                f.write(f"{formatted_analysis.overall_summary}\n\n")
                
                # Analysis by bar
                if formatted_analysis.analysis_by_bar:
                    f.write("ANALYSIS BY BAR\n")
                    f.write("-" * 15 + "\n")
                    
                    for bar_num in sorted(formatted_analysis.analysis_by_bar.keys()):
                        bar_analysis = formatted_analysis.analysis_by_bar[bar_num]
                        f.write(f"Bar {bar_num}:\n")
                        
                        if bar_analysis['scales']:
                            f.write("  Scales:\n")
                            for scale in bar_analysis['scales']:
                                f.write(f"    • {scale['type']} (confidence: {scale['confidence']:.2f}, {scale['time_range']})\n")
                        
                        if bar_analysis['arpeggios']:
                            f.write("  Arpeggios:\n")
                            for arpeggio in bar_analysis['arpeggios']:
                                f.write(f"    • {arpeggio['type']} {arpeggio['direction']} (confidence: {arpeggio['confidence']:.2f}, {arpeggio['time_range']})\n")
                        
                        if bar_analysis['approach_tones']:
                            f.write("  Approach Tones:\n")
                            for approach in bar_analysis['approach_tones']:
                                f.write(f"    • {approach['type']} targeting {approach['target_note']} (confidence: {approach['confidence']:.2f}, {approach['time_range']})\n")
                        
                        f.write("\n")
                
                # Technical notes
                if formatted_analysis.technical_notes:
                    f.write("TECHNICAL NOTES\n")
                    f.write("-" * 15 + "\n")
                    for note in formatted_analysis.technical_notes:
                        f.write(f"• {note}\n")
                    f.write("\n")
                
                # Study recommendations
                if formatted_analysis.study_recommendations:
                    f.write("STUDY RECOMMENDATIONS\n")
                    f.write("-" * 21 + "\n")
                    for recommendation in formatted_analysis.study_recommendations:
                        f.write(f"• {recommendation}\n")
                    f.write("\n")
                
                f.write("End of Analysis Report\n")
                
        except Exception as e:
            raise Exception(f"Error exporting formatted report: {e}")
    
    def display_formatted_report(self, formatted_analysis: FormattedAnalysis) -> None:
        """Display formatted analysis report in the console."""
        print("\n" + "=" * 60)
        print("JAZZ SOLO ANALYSIS REPORT")
        print("=" * 60)
        
        # Basic information
        print(f"\nSOLO INFORMATION")
        print(f"-" * 18)
        print(f"Title: {formatted_analysis.title}")
        print(f"Performer: {formatted_analysis.performer}")
        print(f"Key: {formatted_analysis.key_signature}")
        if formatted_analysis.tempo:
            print(f"Tempo: {formatted_analysis.tempo} BPM")
        
        # Chord changes
        print(f"\nCHORD CHANGES")
        print(f"-" * 13)
        for line in formatted_analysis.chord_changes:
            print(line)
        
        # Overall summary
        print(f"\nOVERALL ANALYSIS SUMMARY")
        print(f"-" * 26)
        print(formatted_analysis.overall_summary)
        
        # Analysis by bar (show first 8 bars as example)
        if formatted_analysis.analysis_by_bar:
            print(f"\nANALYSIS BY BAR (First 8 bars)")
            print(f"-" * 30)
            
            for bar_num in sorted(formatted_analysis.analysis_by_bar.keys())[:8]:
                bar_analysis = formatted_analysis.analysis_by_bar[bar_num]
                print(f"Bar {bar_num}:")
                
                if bar_analysis['scales']:
                    print("  Scales:")
                    for scale in bar_analysis['scales']:
                        print(f"    • {scale['type']} (confidence: {scale['confidence']:.2f})")
                
                if bar_analysis['arpeggios']:
                    print("  Arpeggios:")
                    for arpeggio in bar_analysis['arpeggios']:
                        print(f"    • {arpeggio['type']} {arpeggio['direction']} (confidence: {arpeggio['confidence']:.2f})")
                
                if bar_analysis['approach_tones']:
                    print("  Approach Tones:")
                    for approach in bar_analysis['approach_tones']:
                        print(f"    • {approach['type']} targeting {approach['target_note']} (confidence: {approach['confidence']:.2f})")
                
                print()
        
        # Technical notes
        if formatted_analysis.technical_notes:
            print(f"TECHNICAL NOTES")
            print(f"-" * 15)
            for note in formatted_analysis.technical_notes:
                print(f"• {note}")
        
        # Study recommendations
        if formatted_analysis.study_recommendations:
            print(f"\nSTUDY RECOMMENDATIONS")
            print(f"-" * 21)
            for recommendation in formatted_analysis.study_recommendations:
                print(f"• {recommendation}")
        
        print(f"\n" + "=" * 60)
