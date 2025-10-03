"""
Public Domain Jazz Transcription Client.

This module provides functionality to access and integrate public domain jazz transcriptions
from various sources for analysis and study.
"""

import os
import json
import requests
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import time


@dataclass
class PublicDomainTranscription:
    """Container for public domain transcription data."""
    id: str
    title: str
    performer: str
    composer: str
    key_signature: str
    tempo: Optional[float]
    year: Optional[int]
    source: str
    source_url: str
    file_format: str  # 'musicxml', 'pdf', 'image', 'midi'
    file_path: Optional[str]
    description: str
    tags: List[str]
    difficulty_level: str
    genre: str
    download_date: str
    metadata: Dict[str, Any]


class PublicDomainClient:
    """Client for accessing public domain jazz transcriptions."""
    
    def __init__(self, cache_dir: str = "data/public_domain"):
        """Initialize the public domain client."""
        self.cache_dir = cache_dir
        self.sources = {
            'imslp': {
                'name': 'IMSLP (International Music Score Library Project)',
                'base_url': 'https://imslp.org',
                'search_endpoint': '/api/search',
                'description': 'Classical and jazz scores in public domain'
            },
            'mutopia': {
                'name': 'Mutopia Project',
                'base_url': 'https://www.mutopiaproject.org',
                'search_endpoint': '/cgi-bin/make-table.cgi',
                'description': 'Free sheet music in public domain'
            },
            'cpdl': {
                'name': 'Choral Public Domain Library',
                'base_url': 'https://www.cpdl.org',
                'search_endpoint': '/wiki/index.php',
                'description': 'Choral music including jazz arrangements'
            }
        }
        self._ensure_cache_directory()
    
    def _ensure_cache_directory(self) -> None:
        """Create cache directory if it doesn't exist."""
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Create subdirectories for different file types
        for file_type in ['musicxml', 'pdf', 'images', 'midi', 'metadata']:
            os.makedirs(os.path.join(self.cache_dir, file_type), exist_ok=True)
    
    def search_transcriptions(self, 
                            query: str,
                            source: Optional[str] = None,
                            genre: Optional[str] = None,
                            difficulty: Optional[str] = None,
                            limit: int = 20) -> List[PublicDomainTranscription]:
        """Search for public domain transcriptions."""
        results = []
        
        # For now, return mock data since we don't have actual API access
        # In a real implementation, this would query the actual public domain sources
        mock_results = self._get_mock_transcriptions(query, limit)
        results.extend(mock_results)
        
        return results
    
    def _get_mock_transcriptions(self, query: str, limit: int) -> List[PublicDomainTranscription]:
        """Get mock transcription data for demonstration purposes."""
        mock_data = [
            {
                'id': 'imslp_001',
                'title': 'Blue Moon',
                'performer': 'Lester Young',
                'composer': 'Richard Rodgers',
                'key_signature': 'F Major',
                'tempo': 120.0,
                'year': 1935,
                'source': 'imslp',
                'source_url': 'https://imslp.org/wiki/Blue_Moon_(Rodgers,_Richard)',
                'file_format': 'musicxml',
                'file_path': None,
                'description': 'Classic jazz standard transcription',
                'tags': ['jazz', 'standard', 'ballad', 'saxophone'],
                'difficulty_level': 'Intermediate',
                'genre': 'Jazz',
                'download_date': datetime.now().isoformat(),
                'metadata': {'duration': '3:45', 'instruments': ['saxophone', 'piano']}
            },
            {
                'id': 'mutopia_001',
                'title': 'Autumn Leaves',
                'performer': 'Cannonball Adderley',
                'composer': 'Joseph Kosma',
                'key_signature': 'E Minor',
                'tempo': 140.0,
                'year': 1958,
                'source': 'mutopia',
                'source_url': 'https://www.mutopiaproject.org/cgibin/make-table.cgi?searchingfor=autumn+leaves',
                'file_format': 'pdf',
                'file_path': None,
                'description': 'Bebop interpretation of jazz standard',
                'tags': ['jazz', 'bebop', 'standard', 'alto-saxophone'],
                'difficulty_level': 'Advanced',
                'genre': 'Jazz',
                'download_date': datetime.now().isoformat(),
                'metadata': {'duration': '4:20', 'instruments': ['alto-saxophone', 'rhythm-section']}
            },
            {
                'id': 'cpdl_001',
                'title': 'All the Things You Are',
                'performer': 'Charlie Parker',
                'composer': 'Jerome Kern',
                'key_signature': 'Ab Major',
                'tempo': 160.0,
                'year': 1950,
                'source': 'cpdl',
                'source_url': 'https://www.cpdl.org/wiki/index.php/All_the_Things_You_Are',
                'file_format': 'musicxml',
                'file_path': None,
                'description': 'Bebop master\'s interpretation',
                'tags': ['jazz', 'bebop', 'standard', 'alto-saxophone', 'charlie-parker'],
                'difficulty_level': 'Expert',
                'genre': 'Jazz',
                'download_date': datetime.now().isoformat(),
                'metadata': {'duration': '3:15', 'instruments': ['alto-saxophone', 'piano', 'bass', 'drums']}
            }
        ]
        
        # Filter by query if provided
        if query.lower() in ['jazz', 'standard', 'bebop']:
            filtered_data = [item for item in mock_data if query.lower() in item['tags']]
        else:
            filtered_data = mock_data
        
        # Limit results
        filtered_data = filtered_data[:limit]
        
        # Convert to PublicDomainTranscription objects
        transcriptions = []
        for item in filtered_data:
            transcription = PublicDomainTranscription(**item)
            transcriptions.append(transcription)
        
        return transcriptions
    
    def download_transcription(self, transcription: PublicDomainTranscription) -> bool:
        """Download a transcription file."""
        try:
            # For mock implementation, create a placeholder file
            if transcription.file_format == 'musicxml':
                file_path = os.path.join(self.cache_dir, 'musicxml', f"{transcription.id}.xml")
                self._create_mock_musicxml_file(file_path, transcription)
            elif transcription.file_format == 'pdf':
                file_path = os.path.join(self.cache_dir, 'pdf', f"{transcription.id}.pdf")
                self._create_mock_pdf_file(file_path, transcription)
            else:
                file_path = os.path.join(self.cache_dir, 'metadata', f"{transcription.id}.json")
                self._create_mock_metadata_file(file_path, transcription)
            
            # Update transcription with file path
            transcription.file_path = file_path
            
            # Save transcription metadata
            metadata_path = os.path.join(self.cache_dir, 'metadata', f"{transcription.id}_metadata.json")
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'id': transcription.id,
                    'title': transcription.title,
                    'performer': transcription.performer,
                    'composer': transcription.composer,
                    'key_signature': transcription.key_signature,
                    'tempo': transcription.tempo,
                    'year': transcription.year,
                    'source': transcription.source,
                    'source_url': transcription.source_url,
                    'file_format': transcription.file_format,
                    'file_path': file_path,
                    'description': transcription.description,
                    'tags': transcription.tags,
                    'difficulty_level': transcription.difficulty_level,
                    'genre': transcription.genre,
                    'download_date': transcription.download_date,
                    'metadata': transcription.metadata
                }, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Error downloading transcription: {e}")
            return False
    
    def _create_mock_musicxml_file(self, file_path: str, transcription: PublicDomainTranscription) -> None:
        """Create a mock MusicXML file for demonstration."""
        # Create a basic MusicXML structure
        musicxml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="3.1">
  <work>
    <work-title>{transcription.title}</work-title>
  </work>
  <identification>
    <creator type="composer">{transcription.composer}</creator>
    <creator type="arranger">{transcription.performer}</creator>
  </identification>
  <part-list>
    <score-part id="P1">
      <part-name>Saxophone</part-name>
    </score-part>
  </part-list>
  <part id="P1">
    <measure number="1">
      <attributes>
        <divisions>1</divisions>
        <key>
          <fifths>0</fifths>
          <mode>major</mode>
        </key>
        <time>
          <beats>4</beats>
          <beat-type>4</beat-type>
        </time>
        <clef>
          <sign>G</sign>
          <line>2</line>
        </clef>
      </attributes>
      <note>
        <pitch>
          <step>C</step>
          <octave>4</octave>
        </pitch>
        <duration>4</duration>
        <type>whole</type>
      </note>
    </measure>
  </part>
</score-partwise>"""
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(musicxml_content)
    
    def _create_mock_pdf_file(self, file_path: str, transcription: PublicDomainTranscription) -> None:
        """Create a mock PDF file for demonstration."""
        # Create a simple text file as placeholder for PDF
        pdf_content = f"""Mock PDF Content for {transcription.title}
Performer: {transcription.performer}
Composer: {transcription.composer}
Key: {transcription.key_signature}
Tempo: {transcription.tempo} BPM

This is a placeholder file representing a PDF transcription.
In a real implementation, this would be an actual PDF file.
"""
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(pdf_content)
    
    def _create_mock_metadata_file(self, file_path: str, transcription: PublicDomainTranscription) -> None:
        """Create a mock metadata file."""
        metadata = {
            'transcription': transcription.__dict__,
            'created_at': datetime.now().isoformat(),
            'file_type': 'metadata'
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    def get_downloaded_transcriptions(self) -> List[PublicDomainTranscription]:
        """Get list of downloaded transcriptions."""
        transcriptions = []
        metadata_dir = os.path.join(self.cache_dir, 'metadata')
        
        if not os.path.exists(metadata_dir):
            return transcriptions
        
        for filename in os.listdir(metadata_dir):
            if filename.endswith('_metadata.json'):
                try:
                    with open(os.path.join(metadata_dir, filename), 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    transcription = PublicDomainTranscription(**data)
                    transcriptions.append(transcription)
                except Exception as e:
                    print(f"Error loading transcription metadata {filename}: {e}")
        
        return transcriptions
    
    def get_available_sources(self) -> Dict[str, Dict[str, str]]:
        """Get information about available public domain sources."""
        return self.sources
    
    def get_transcription_by_id(self, transcription_id: str) -> Optional[PublicDomainTranscription]:
        """Get a specific transcription by ID."""
        downloaded_transcriptions = self.get_downloaded_transcriptions()
        
        for transcription in downloaded_transcriptions:
            if transcription.id == transcription_id:
                return transcription
        
        return None
    
    def delete_transcription(self, transcription_id: str) -> bool:
        """Delete a downloaded transcription."""
        try:
            transcription = self.get_transcription_by_id(transcription_id)
            if not transcription:
                return False
            
            # Delete the main file
            if transcription.file_path and os.path.exists(transcription.file_path):
                os.remove(transcription.file_path)
            
            # Delete metadata file
            metadata_path = os.path.join(self.cache_dir, 'metadata', f"{transcription_id}_metadata.json")
            if os.path.exists(metadata_path):
                os.remove(metadata_path)
            
            return True
            
        except Exception as e:
            print(f"Error deleting transcription: {e}")
            return False
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get statistics about cached transcriptions."""
        stats = {
            'total_transcriptions': 0,
            'by_source': {},
            'by_format': {},
            'by_difficulty': {},
            'total_size_mb': 0
        }
        
        downloaded_transcriptions = self.get_downloaded_transcriptions()
        stats['total_transcriptions'] = len(downloaded_transcriptions)
        
        for transcription in downloaded_transcriptions:
            # Count by source
            source = transcription.source
            stats['by_source'][source] = stats['by_source'].get(source, 0) + 1
            
            # Count by format
            file_format = transcription.file_format
            stats['by_format'][file_format] = stats['by_format'].get(file_format, 0) + 1
            
            # Count by difficulty
            difficulty = transcription.difficulty_level
            stats['by_difficulty'][difficulty] = stats['by_difficulty'].get(difficulty, 0) + 1
            
            # Calculate file size
            if transcription.file_path and os.path.exists(transcription.file_path):
                file_size = os.path.getsize(transcription.file_path)
                stats['total_size_mb'] += file_size / (1024 * 1024)
        
        stats['total_size_mb'] = round(stats['total_size_mb'], 2)
        
        return stats
