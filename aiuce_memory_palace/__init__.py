"""
Memory Palace - Raw Verbatim Memory Storage.

A memory palace implementation based on the ancient Greek memory technique.
Stores complete original conversations without summarization (Raw Verbatim philosophy).

Key features:
- Raw Verbatim storage (no information loss)
- Spatial indexing (Wing → Hall → Room → Closet)
- Timeline retrieval
- Hash chain integrity verification

Usage:
    from aiuce_memory_palace import PalaceMemory, PalaceWing
    
    palace = PalaceMemory()
    palace.remember("Hello, how are you?", wing=PalaceWing.LIFE)
    results = palace.recall("hello")
"""

from .types import PalaceWing, MemoryRecord
from .palace import PalaceEngine, MemoryRoom, PalaceMemory

__version__ = "0.1.0"

__all__ = [
    # Types
    "PalaceWing",
    "MemoryRecord",
    # Core
    "PalaceEngine",
    "MemoryRoom",
    # Facade
    "PalaceMemory",
]
