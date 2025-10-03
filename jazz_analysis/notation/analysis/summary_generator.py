"""
Analysis Summary Generator for Jazz Solo Analysis.

This module combines results from scale, arpeggio, and approach tone analysis
to generate comprehensive plain English summaries with high-level musical insights.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import os


@dataclass
class AnalysisSummary:
    """Container for comprehensive analysis summary."""
    solo_title: str
    performer: str
    key_signature: str
    tempo: Optional[float]
    total_notes: int
    analysis_coverage: Dict[str, float]  # coverage percentages for each analysis type
    scale_insights: List[str]
    arpeggio_insights: List[str]
    approach_insights: List[str]
    overall_character: str
    technical_level: str
    harmonic_sophistication: str
    melodic_characteristics: List[str]
    recommendations: List[str]


class JazzAnalysisSummaryGenerator:
    """Generates comprehensive analysis summaries from multiple analysis results."""
    
    def __init__(self):
        """Initialize the summary generator."""
        self.scale_patterns = {
            'harmonic_minor': 'Harmonic minor scales',
            'diminished': 'Diminished scales',
            'whole_tone': 'Whole tone scales',
            'pentatonic': 'Pentatonic scales',
            'bebop': 'Bebop scales',
            'blues': 'Blues scales'
        }
        
        self.arpeggio_types = {
            'minor_6': 'Minor 6th arpeggios',
            'triads': 'Triadic arpeggios',
            'seventh_chords': '7th chord arpeggios',
            'extended_chords': 'Extended chord arpeggios'
        }
        
        self.approach_patterns = {
            'chromatic_enclosure': 'Chromatic enclosures',
            'diminished_burst': 'Diminished bursts',
            'neighbor_tones': 'Neighbor tone approaches',
            'passing_tones': 'Passing tone approaches'
        }
    
    def generate_summary(self, 
                        scale_analysis: Any,
                        arpeggio_analysis: Any, 
                        approach_analysis: Any,
                        solo_metadata: Dict[str, Any]) -> AnalysisSummary:
        """Generate comprehensive analysis summary from all analysis results."""
        
        # Extract basic metadata
        solo_title = solo_metadata.get('title', 'Unknown Solo')
        performer = solo_metadata.get('performer', 'Unknown Performer')
        key_signature = solo_metadata.get('key', 'Unknown Key')
        tempo = solo_metadata.get('tempo')
        total_notes = solo_metadata.get('total_notes', 0)
        
        # Calculate analysis coverage
        analysis_coverage = self._calculate_coverage(scale_analysis, arpeggio_analysis, approach_analysis)
        
        # Generate insights for each analysis type
        scale_insights = self._generate_scale_insights(scale_analysis)
        arpeggio_insights = self._generate_arpeggio_insights(arpeggio_analysis)
        approach_insights = self._generate_approach_insights(approach_analysis)
        
        # Generate overall character assessment
        overall_character = self._assess_overall_character(scale_insights, arpeggio_insights, approach_insights)
        technical_level = self._assess_technical_level(analysis_coverage, total_notes)
        harmonic_sophistication = self._assess_harmonic_sophistication(arpeggio_analysis, approach_analysis)
        
        # Generate melodic characteristics
        melodic_characteristics = self._generate_melodic_characteristics(
            scale_analysis, arpeggio_analysis, approach_analysis
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            analysis_coverage, scale_insights, arpeggio_insights, approach_insights
        )
        
        return AnalysisSummary(
            solo_title=solo_title,
            performer=performer,
            key_signature=key_signature,
            tempo=tempo,
            total_notes=total_notes,
            analysis_coverage=analysis_coverage,
            scale_insights=scale_insights,
            arpeggio_insights=arpeggio_insights,
            approach_insights=approach_insights,
            overall_character=overall_character,
            technical_level=technical_level,
            harmonic_sophistication=harmonic_sophistication,
            melodic_characteristics=melodic_characteristics,
            recommendations=recommendations
        )
    
    def _calculate_coverage(self, scale_analysis: Any, arpeggio_analysis: Any, approach_analysis: Any) -> Dict[str, float]:
        """Calculate coverage percentages for each analysis type."""
        coverage = {}
        
        if hasattr(scale_analysis, 'scale_coverage'):
            coverage['scales'] = scale_analysis.scale_coverage
        else:
            coverage['scales'] = 0.0
            
        if hasattr(arpeggio_analysis, 'arpeggio_coverage'):
            coverage['arpeggios'] = arpeggio_analysis.arpeggio_coverage
        else:
            coverage['arpeggios'] = 0.0
            
        if hasattr(approach_analysis, 'approach_coverage'):
            coverage['approach_tones'] = approach_analysis.approach_coverage
        else:
            coverage['approach_tones'] = 0.0
        
        return coverage
    
    def _generate_scale_insights(self, scale_analysis: Any) -> List[str]:
        """Generate insights about scale usage."""
        insights = []
        
        if not hasattr(scale_analysis, 'detected_scales') or not scale_analysis.detected_scales:
            insights.append("No significant scale patterns detected.")
            return insights
        
        # Count scale types
        scale_counts = {}
        for scale in scale_analysis.detected_scales:
            scale_type = scale.scale_type
            scale_counts[scale_type] = scale_counts.get(scale_type, 0) + 1
        
        # Generate insights based on scale usage
        if scale_counts:
            most_common = max(scale_counts.items(), key=lambda x: x[1])
            insights.append(f"Most prominent scale: {self.scale_patterns.get(most_common[0], most_common[0])} ({most_common[1]} occurrences)")
        
        if len(scale_counts) > 3:
            insights.append("Demonstrates sophisticated scale vocabulary with multiple scale types.")
        elif len(scale_counts) == 1:
            insights.append("Focused approach using primarily one scale type.")
        
        # Check for jazz-specific scales
        jazz_scales = ['bebop', 'blues', 'harmonic_minor', 'diminished', 'whole_tone']
        jazz_usage = sum(scale_counts.get(scale, 0) for scale in jazz_scales)
        if jazz_usage > 0:
            insights.append(f"Strong jazz vocabulary with {jazz_usage} jazz-specific scale patterns.")
        
        return insights
    
    def _generate_arpeggio_insights(self, arpeggio_analysis: Any) -> List[str]:
        """Generate insights about arpeggio usage."""
        insights = []
        
        if not hasattr(arpeggio_analysis, 'detected_arpeggios') or not arpeggio_analysis.detected_arpeggios:
            insights.append("No significant arpeggio patterns detected.")
            return insights
        
        # Count arpeggio types
        arpeggio_counts = {}
        for arpeggio in arpeggio_analysis.detected_arpeggios:
            arpeggio_type = arpeggio.arpeggio_type
            arpeggio_counts[arpeggio_type] = arpeggio_counts.get(arpeggio_type, 0) + 1
        
        if arpeggio_counts:
            most_common = max(arpeggio_counts.items(), key=lambda x: x[1])
            insights.append(f"Most prominent arpeggio: {self.arpeggio_types.get(most_common[0], most_common[0])} ({most_common[1]} occurrences)")
        
        # Check for extended chord usage
        if 'extended_chords' in arpeggio_counts:
            insights.append("Demonstrates advanced harmonic vocabulary with extended chord arpeggios.")
        
        # Check for direction patterns
        ascending = sum(1 for a in arpeggio_analysis.detected_arpeggios if a.direction == 'ascending')
        descending = sum(1 for a in arpeggio_analysis.detected_arpeggios if a.direction == 'descending')
        
        if ascending > descending * 1.5:
            insights.append("Preference for ascending arpeggio patterns.")
        elif descending > ascending * 1.5:
            insights.append("Preference for descending arpeggio patterns.")
        
        return insights
    
    def _generate_approach_insights(self, approach_analysis: Any) -> List[str]:
        """Generate insights about approach tone usage."""
        insights = []
        
        if not hasattr(approach_analysis, 'detected_patterns') or not approach_analysis.detected_patterns:
            insights.append("No significant approach tone patterns detected.")
            return insights
        
        # Count approach pattern types
        pattern_counts = {}
        for pattern in approach_analysis.detected_patterns:
            pattern_type = pattern.pattern_type
            pattern_counts[pattern_type] = pattern_counts.get(pattern_type, 0) + 1
        
        if pattern_counts:
            most_common = max(pattern_counts.items(), key=lambda x: x[1])
            insights.append(f"Most prominent approach: {self.approach_patterns.get(most_common[0], most_common[0])} ({most_common[1]} occurrences)")
        
        # Check for chromatic sophistication
        chromatic_patterns = ['chromatic_enclosure', 'diminished_burst']
        chromatic_usage = sum(pattern_counts.get(pattern, 0) for pattern in chromatic_patterns)
        if chromatic_usage > 0:
            insights.append(f"Sophisticated chromatic approach technique with {chromatic_usage} chromatic patterns.")
        
        # Check for target note variety
        if hasattr(approach_analysis, 'target_notes') and approach_analysis.target_notes:
            unique_targets = len(approach_analysis.target_notes)
            if unique_targets > 5:
                insights.append(f"Diverse target note selection with {unique_targets} different target notes.")
        
        return insights
    
    def _assess_overall_character(self, scale_insights: List[str], arpeggio_insights: List[str], approach_insights: List[str]) -> str:
        """Assess the overall character of the solo."""
        total_insights = len(scale_insights) + len(arpeggio_insights) + len(approach_insights)
        
        if total_insights <= 3:
            return "Straightforward and direct melodic approach"
        elif total_insights <= 6:
            return "Balanced mix of traditional and modern jazz vocabulary"
        else:
            return "Sophisticated and complex jazz vocabulary with advanced techniques"
    
    def _assess_technical_level(self, coverage: Dict[str, float], total_notes: int) -> str:
        """Assess the technical level of the solo."""
        avg_coverage = sum(coverage.values()) / len(coverage) if coverage else 0
        
        if avg_coverage < 20:
            return "Beginner to Intermediate"
        elif avg_coverage < 40:
            return "Intermediate to Advanced"
        else:
            return "Advanced to Professional"
    
    def _assess_harmonic_sophistication(self, arpeggio_analysis: Any, approach_analysis: Any) -> str:
        """Assess harmonic sophistication level."""
        sophistication_score = 0
        
        # Check for extended chord arpeggios
        if hasattr(arpeggio_analysis, 'detected_arpeggios'):
            extended_count = sum(1 for a in arpeggio_analysis.detected_arpeggios if a.arpeggio_type == 'extended_chords')
            if extended_count > 0:
                sophistication_score += 2
        
        # Check for chromatic approach patterns
        if hasattr(approach_analysis, 'detected_patterns'):
            chromatic_count = sum(1 for p in approach_analysis.detected_patterns if 'chromatic' in p.pattern_type)
            if chromatic_count > 0:
                sophistication_score += 1
        
        if sophistication_score == 0:
            return "Basic harmonic vocabulary"
        elif sophistication_score <= 2:
            return "Intermediate harmonic sophistication"
        else:
            return "Advanced harmonic sophistication"
    
    def _generate_melodic_characteristics(self, scale_analysis: Any, arpeggio_analysis: Any, approach_analysis: Any) -> List[str]:
        """Generate melodic characteristics summary."""
        characteristics = []
        
        # Analyze melodic density
        if hasattr(scale_analysis, 'detected_scales') and scale_analysis.detected_scales:
            characteristics.append("Scale-based melodic development")
        
        if hasattr(arpeggio_analysis, 'detected_arpeggios') and arpeggio_analysis.detected_arpeggios:
            characteristics.append("Arpeggio-based harmonic outlining")
        
        if hasattr(approach_analysis, 'detected_patterns') and approach_analysis.detected_patterns:
            characteristics.append("Approach tone-based melodic embellishment")
        
        # Check for mixed approach
        analysis_types = sum([
            bool(hasattr(scale_analysis, 'detected_scales') and scale_analysis.detected_scales),
            bool(hasattr(arpeggio_analysis, 'detected_arpeggios') and arpeggio_analysis.detected_arpeggios),
            bool(hasattr(approach_analysis, 'detected_patterns') and approach_analysis.detected_patterns)
        ])
        
        if analysis_types >= 2:
            characteristics.append("Mixed melodic approach combining multiple techniques")
        
        return characteristics
    
    def _generate_recommendations(self, coverage: Dict[str, float], scale_insights: List[str], arpeggio_insights: List[str], approach_insights: List[str]) -> List[str]:
        """Generate practice and study recommendations."""
        recommendations = []
        
        # Coverage-based recommendations
        if coverage.get('scales', 0) < 30:
            recommendations.append("Focus on scale practice to improve melodic vocabulary")
        
        if coverage.get('arpeggios', 0) < 20:
            recommendations.append("Practice arpeggios to strengthen harmonic awareness")
        
        if coverage.get('approach_tones', 0) < 15:
            recommendations.append("Study approach tone patterns for melodic embellishment")
        
        # Technique-specific recommendations
        if not any('jazz' in insight.lower() for insight in scale_insights):
            recommendations.append("Explore jazz-specific scales (bebop, blues, diminished)")
        
        if not any('extended' in insight.lower() for insight in arpeggio_insights):
            recommendations.append("Practice extended chord arpeggios (9th, 11th, 13th)")
        
        if not any('chromatic' in insight.lower() for insight in approach_insights):
            recommendations.append("Study chromatic approach patterns and enclosures")
        
        return recommendations
    
    def export_summary(self, summary: AnalysisSummary, output_path: str) -> None:
        """Export analysis summary to a formatted text file."""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("JAZZ SOLO ANALYSIS SUMMARY\n")
                f.write("=" * 50 + "\n\n")
                
                # Basic information
                f.write(f"Solo: {summary.solo_title}\n")
                f.write(f"Performer: {summary.performer}\n")
                f.write(f"Key: {summary.key_signature}\n")
                if summary.tempo:
                    f.write(f"Tempo: {summary.tempo} BPM\n")
                f.write(f"Total Notes: {summary.total_notes}\n\n")
                
                # Analysis coverage
                f.write("ANALYSIS COVERAGE\n")
                f.write("-" * 20 + "\n")
                for analysis_type, coverage in summary.analysis_coverage.items():
                    f.write(f"{analysis_type.replace('_', ' ').title()}: {coverage:.1f}%\n")
                f.write("\n")
                
                # Overall assessment
                f.write("OVERALL ASSESSMENT\n")
                f.write("-" * 20 + "\n")
                f.write(f"Character: {summary.overall_character}\n")
                f.write(f"Technical Level: {summary.technical_level}\n")
                f.write(f"Harmonic Sophistication: {summary.harmonic_sophistication}\n\n")
                
                # Scale insights
                f.write("SCALE ANALYSIS\n")
                f.write("-" * 15 + "\n")
                for insight in summary.scale_insights:
                    f.write(f"• {insight}\n")
                f.write("\n")
                
                # Arpeggio insights
                f.write("ARPEGGIO ANALYSIS\n")
                f.write("-" * 17 + "\n")
                for insight in summary.arpeggio_insights:
                    f.write(f"• {insight}\n")
                f.write("\n")
                
                # Approach tone insights
                f.write("APPROACH TONE ANALYSIS\n")
                f.write("-" * 22 + "\n")
                for insight in summary.approach_insights:
                    f.write(f"• {insight}\n")
                f.write("\n")
                
                # Melodic characteristics
                f.write("MELODIC CHARACTERISTICS\n")
                f.write("-" * 23 + "\n")
                for characteristic in summary.melodic_characteristics:
                    f.write(f"• {characteristic}\n")
                f.write("\n")
                
                # Recommendations
                f.write("STUDY RECOMMENDATIONS\n")
                f.write("-" * 21 + "\n")
                for recommendation in summary.recommendations:
                    f.write(f"• {recommendation}\n")
                f.write("\n")
                
                f.write("Analysis completed successfully.\n")
                
        except Exception as e:
            raise Exception(f"Error exporting summary: {e}")
