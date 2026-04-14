"""
Type definitions for Memory Palace.

Core data structures: PalaceWing enum, MemoryRecord dataclass.
"""

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import hashlib


class PalaceWing(Enum):
    """
    Palace Wing (Level 1 spatial category).
    Analogous to rooms in the memory palace technique.
    """
    PEOPLE = "people"        # People: conversations with others
    PROJECTS = "projects"    # Projects: work/project related
    LEARNING = "learning"    # Learning: books/courses/research
    HEALTH = "health"       # Health: body/medical/fitness
    FINANCE = "finance"      # Finance: money/investments/taxes
    LIFE = "life"           # Life: daily/family/travel
    REFLECTION = "reflection"  # Reflection: decisions/experience/lessons
    GENERAL = "general"     # General: uncategorized


@dataclass
class MemoryRecord:
    """
    Memory Record - Raw Verbatim storage.
    
    Stores complete original conversation without filtering.
    Includes hash chain for integrity verification.
    """
    record_id: str
    room_id: str
    raw_text: str                    # Original text (Raw Verbatim, unfiltered)
    speaker: str = ""                # Speaker: human/agent/system
    timestamp: datetime = field(default_factory=datetime.now)
    hash_chain: Optional[str] = None  # Hash chain (previous record hash)
    metadata: Dict[str, Any] = field(default_factory=dict)  # wing/hall/closet index
    tags: Set[str] = field(default_factory=set)
    sources: List[str] = field(default_factory=list)  # Source file paths/URLs

    @staticmethod
    def compute_hash(text: str, prev_hash: Optional[str] = None) -> str:
        """Compute SHA-256 hash (for hash chain integrity)."""
        content = f"{prev_hash or 'GENESIS'}:{text}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def verify_chain(self, prev_record: Optional["MemoryRecord"]) -> bool:
        """Verify hash chain integrity."""
        expected = self.compute_hash(
            self.raw_text, 
            prev_record.hash_chain if prev_record else None
        )
        return self.hash_chain == expected
