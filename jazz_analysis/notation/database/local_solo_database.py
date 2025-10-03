"""
Local Solo Database for Jazz Analysis.

This module provides functionality to store, manage, and retrieve analyzed jazz solos
in a local SQLite database for easy access and organization.
"""

import sqlite3
import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class SoloRecord:
    """Container for solo database record."""
    id: Optional[int]
    title: str
    performer: str
    key_signature: str
    tempo: Optional[float]
    source_type: str  # 'weimar', 'musicxml', 'notation'
    source_id: str
    total_notes: int
    analysis_date: str
    scale_coverage: float
    arpeggio_coverage: float
    approach_coverage: float
    technical_level: str
    harmonic_sophistication: str
    overall_character: str
    chord_changes: str
    analysis_summary: str
    formatted_report_path: str
    metadata: Dict[str, Any]


class LocalSoloDatabase:
    """Local database for storing and managing analyzed jazz solos."""
    
    def __init__(self, db_path: str = "data/local_solos.db"):
        """Initialize the local solo database."""
        self.db_path = db_path
        self._ensure_database_exists()
    
    def _ensure_database_exists(self) -> None:
        """Create database and tables if they don't exist."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create solos table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS solos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    performer TEXT NOT NULL,
                    key_signature TEXT NOT NULL,
                    tempo REAL,
                    source_type TEXT NOT NULL,
                    source_id TEXT NOT NULL,
                    total_notes INTEGER NOT NULL,
                    analysis_date TEXT NOT NULL,
                    scale_coverage REAL NOT NULL,
                    arpeggio_coverage REAL NOT NULL,
                    approach_coverage REAL NOT NULL,
                    technical_level TEXT NOT NULL,
                    harmonic_sophistication TEXT NOT NULL,
                    overall_character TEXT NOT NULL,
                    chord_changes TEXT,
                    analysis_summary TEXT,
                    formatted_report_path TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_solos_performer 
                ON solos(performer)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_solos_source_type 
                ON solos(source_type)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_solos_technical_level 
                ON solos(technical_level)
            """)
            
            conn.commit()
    
    def add_solo(self, solo_record: SoloRecord) -> int:
        """Add a new solo to the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO solos (
                    title, performer, key_signature, tempo, source_type, source_id,
                    total_notes, analysis_date, scale_coverage, arpeggio_coverage,
                    approach_coverage, technical_level, harmonic_sophistication,
                    overall_character, chord_changes, analysis_summary,
                    formatted_report_path, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                solo_record.title,
                solo_record.performer,
                solo_record.key_signature,
                solo_record.tempo,
                solo_record.source_type,
                solo_record.source_id,
                solo_record.total_notes,
                solo_record.analysis_date,
                solo_record.scale_coverage,
                solo_record.arpeggio_coverage,
                solo_record.approach_coverage,
                solo_record.technical_level,
                solo_record.harmonic_sophistication,
                solo_record.overall_character,
                solo_record.chord_changes,
                solo_record.analysis_summary,
                solo_record.formatted_report_path,
                json.dumps(solo_record.metadata)
            ))
            
            solo_id = cursor.lastrowid
            conn.commit()
            return solo_id
    
    def get_solo(self, solo_id: int) -> Optional[SoloRecord]:
        """Get a solo by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, title, performer, key_signature, tempo, source_type, source_id,
                       total_notes, analysis_date, scale_coverage, arpeggio_coverage,
                       approach_coverage, technical_level, harmonic_sophistication,
                       overall_character, chord_changes, analysis_summary,
                       formatted_report_path, metadata
                FROM solos WHERE id = ?
            """, (solo_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return self._row_to_solo_record(row)
    
    def get_all_solos(self) -> List[SoloRecord]:
        """Get all solos in the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, title, performer, key_signature, tempo, source_type, source_id,
                       total_notes, analysis_date, scale_coverage, arpeggio_coverage,
                       approach_coverage, technical_level, harmonic_sophistication,
                       overall_character, chord_changes, analysis_summary,
                       formatted_report_path, metadata
                FROM solos ORDER BY created_at DESC
            """)
            
            rows = cursor.fetchall()
            return [self._row_to_solo_record(row) for row in rows]
    
    def search_solos(self, 
                    performer: Optional[str] = None,
                    source_type: Optional[str] = None,
                    technical_level: Optional[str] = None,
                    harmonic_sophistication: Optional[str] = None) -> List[SoloRecord]:
        """Search solos by various criteria."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Build dynamic query
            conditions = []
            params = []
            
            if performer:
                conditions.append("performer LIKE ?")
                params.append(f"%{performer}%")
            
            if source_type:
                conditions.append("source_type = ?")
                params.append(source_type)
            
            if technical_level:
                conditions.append("technical_level = ?")
                params.append(technical_level)
            
            if harmonic_sophistication:
                conditions.append("harmonic_sophistication = ?")
                params.append(harmonic_sophistication)
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            cursor.execute(f"""
                SELECT id, title, performer, key_signature, tempo, source_type, source_id,
                       total_notes, analysis_date, scale_coverage, arpeggio_coverage,
                       approach_coverage, technical_level, harmonic_sophistication,
                       overall_character, chord_changes, analysis_summary,
                       formatted_report_path, metadata
                FROM solos WHERE {where_clause} ORDER BY created_at DESC
            """, params)
            
            rows = cursor.fetchall()
            return [self._row_to_solo_record(row) for row in rows]
    
    def update_solo(self, solo_id: int, solo_record: SoloRecord) -> bool:
        """Update an existing solo."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE solos SET
                    title = ?, performer = ?, key_signature = ?, tempo = ?,
                    source_type = ?, source_id = ?, total_notes = ?, analysis_date = ?,
                    scale_coverage = ?, arpeggio_coverage = ?, approach_coverage = ?,
                    technical_level = ?, harmonic_sophistication = ?, overall_character = ?,
                    chord_changes = ?, analysis_summary = ?, formatted_report_path = ?,
                    metadata = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                solo_record.title,
                solo_record.performer,
                solo_record.key_signature,
                solo_record.tempo,
                solo_record.source_type,
                solo_record.source_id,
                solo_record.total_notes,
                solo_record.analysis_date,
                solo_record.scale_coverage,
                solo_record.arpeggio_coverage,
                solo_record.approach_coverage,
                solo_record.technical_level,
                solo_record.harmonic_sophistication,
                solo_record.overall_character,
                solo_record.chord_changes,
                solo_record.analysis_summary,
                solo_record.formatted_report_path,
                json.dumps(solo_record.metadata),
                solo_id
            ))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_solo(self, solo_id: int) -> bool:
        """Delete a solo from the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM solos WHERE id = ?", (solo_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total solos
            cursor.execute("SELECT COUNT(*) FROM solos")
            total_solos = cursor.fetchone()[0]
            
            # Solos by source type
            cursor.execute("""
                SELECT source_type, COUNT(*) 
                FROM solos 
                GROUP BY source_type
            """)
            by_source = dict(cursor.fetchall())
            
            # Solos by technical level
            cursor.execute("""
                SELECT technical_level, COUNT(*) 
                FROM solos 
                GROUP BY technical_level
            """)
            by_technical = dict(cursor.fetchall())
            
            # Solos by harmonic sophistication
            cursor.execute("""
                SELECT harmonic_sophistication, COUNT(*) 
                FROM solos 
                GROUP BY harmonic_sophistication
            """)
            by_harmonic = dict(cursor.fetchall())
            
            # Average coverage
            cursor.execute("""
                SELECT 
                    AVG(scale_coverage) as avg_scale,
                    AVG(arpeggio_coverage) as avg_arpeggio,
                    AVG(approach_coverage) as avg_approach
                FROM solos
            """)
            avg_coverage = cursor.fetchone()
            
            return {
                'total_solos': total_solos,
                'by_source_type': by_source,
                'by_technical_level': by_technical,
                'by_harmonic_sophistication': by_harmonic,
                'average_coverage': {
                    'scale': avg_coverage[0] or 0,
                    'arpeggio': avg_coverage[1] or 0,
                    'approach': avg_coverage[2] or 0
                }
            }
    
    def _row_to_solo_record(self, row: Tuple) -> SoloRecord:
        """Convert database row to SoloRecord."""
        metadata = json.loads(row[18]) if row[18] else {}
        
        return SoloRecord(
            id=row[0],
            title=row[1],
            performer=row[2],
            key_signature=row[3],
            tempo=row[4],
            source_type=row[5],
            source_id=row[6],
            total_notes=row[7],
            analysis_date=row[8],
            scale_coverage=row[9],
            arpeggio_coverage=row[10],
            approach_coverage=row[11],
            technical_level=row[12],
            harmonic_sophistication=row[13],
            overall_character=row[14],
            chord_changes=row[15],
            analysis_summary=row[16],
            formatted_report_path=row[17],
            metadata=metadata
        )
    
    def export_solo_data(self, output_path: str) -> None:
        """Export all solo data to a JSON file."""
        solos = self.get_all_solos()
        solo_data = []
        
        for solo in solos:
            solo_dict = asdict(solo)
            solo_data.append(solo_dict)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                'export_date': datetime.now().isoformat(),
                'total_solos': len(solo_data),
                'solos': solo_data
            }, f, indent=2, ensure_ascii=False)
    
    def import_solo_data(self, input_path: str) -> int:
        """Import solo data from a JSON file."""
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        imported_count = 0
        
        for solo_data in data.get('solos', []):
            # Remove id to let database assign new one
            if 'id' in solo_data:
                del solo_data['id']
            
            solo_record = SoloRecord(**solo_data)
            self.add_solo(solo_record)
            imported_count += 1
        
        return imported_count
