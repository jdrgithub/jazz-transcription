"""
Client for accessing the Weimar Jazz Database.
"""

import requests
import os
import tempfile
from contextlib import closing
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class WeimarJazzClient:
    """Client for accessing jazz transcriptions from the Weimar Jazz Database."""
    
    def __init__(self):
        """Initialize the Weimar Jazz Database client."""
        self.base_url = "https://jazzomat.hfm-weimar.de"
        self.database_url = f"{self.base_url}/download/downloads/wjazzd.db"
        self.session = requests.Session()
    
    def search_transcriptions(self, query: str) -> List[Dict]:
        """
        Search for transcriptions in the Weimar Jazz Database.
        
        Args:
            query: Search query string
            
        Returns:
            List of transcription metadata
        """
        logger.info(f"Searching for transcriptions with query: {query}")
        # TODO: Implement actual API call
        return []
    
    def get_transcription(self, transcription_id: str) -> Optional[Dict]:
        """
        Get a specific transcription by ID.
        
        Args:
            transcription_id: ID of the transcription to retrieve
            
        Returns:
            Transcription data or None if not found
        """
        logger.info(f"Retrieving transcription: {transcription_id}")
        # TODO: Implement actual API call
        return None
    
    def download_database(self, output_path: str) -> bool:
        """
        Download the Weimar Jazz Database.
        
        Args:
            output_path: Path where to save the database file
            
        Returns:
            True if download successful, False otherwise
        """
        logger.info(f"Downloading Weimar Jazz Database to {output_path}")
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Create temporary file for atomic write
        temp_fd, temp_path = tempfile.mkstemp(dir=output_dir, suffix='.tmp')
        
        try:
            with closing(self.session.get(
                self.database_url, 
                stream=True, 
                timeout=(5, 60)
            )) as response:
                response.raise_for_status()
                
                with os.fdopen(temp_fd, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:  # filter out keep-alive chunks
                            f.write(chunk)
            
            # Atomic move to final location
            os.replace(temp_path, output_path)
            logger.info(f"Successfully downloaded database to {output_path}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error downloading database: {e}", exc_info=True)
            return False
        except OSError as e:
            logger.error(f"Filesystem error downloading database: {e}", exc_info=True)
            return False
        finally:
            # Clean up temp file if it still exists
            if os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except OSError:
                    pass 