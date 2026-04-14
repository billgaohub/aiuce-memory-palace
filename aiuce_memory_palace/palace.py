"""
Memory Palace Engine.

Core storage and retrieval system using the memory palace technique.
- Raw Verbatim storage (no summarization)
- Spatial indexing (Wing → Hall → Room → Closet)
- Timeline retrieval
- Hash chain integrity
"""

from typing import Dict, Any, List, Optional, Set, Tuple
from datetime import datetime, timedelta
from enum import Enum
import re
import os
import json
import hashlib
import logging
from pathlib import Path
from collections import defaultdict

from .types import PalaceWing, MemoryRecord

logger = logging.getLogger(__name__)


class MemoryRoom:
    """
    Memory Room - A specific topic/project/concept's conversation collection.
    """
    def __init__(
        self,
        room_id: str,
        name: str,
        wing: PalaceWing,
        hall: str = "general",
        closet: str = "",
        description: str = "",
    ):
        self.room_id = room_id
        self.name = name
        self.wing = wing
        self.hall = hall
        self.closet = closet
        self.description = description
        self.records: List[MemoryRecord] = []
        self.created_at = datetime.now()
        self.last_accessed = datetime.now()
        self.tags: Set[str] = set()

    def add(self, record: MemoryRecord):
        self.records.append(record)
        self.last_accessed = datetime.now()

    def get_records(
        self, 
        since: datetime = None, 
        until: datetime = None
    ) -> List[MemoryRecord]:
        records = self.records
        if since:
            records = [r for r in records if r.timestamp >= since]
        if until:
            records = [r for r in records if r.timestamp <= until]
        return records

    def search(self, query: str) -> List[Tuple[MemoryRecord, float]]:
        """
        Keyword-based search within the room.
        Returns: [(record, match_score)]
        """
        query_words = set(re.findall(r'[\w\u4e00-\u9fff]{2,}', query.lower()))
        results = []
        for record in self.records:
            body_words = set(re.findall(r'[\w\u4e00-\u9fff]{2,}', record.raw_text.lower()))
            overlap = query_words & body_words
            if overlap:
                score = len(overlap) / max(len(query_words), 1)
                results.append((record, score))
        return sorted(results, key=lambda x: -x[1])


class PalaceEngine:
    """
    Memory Palace Engine.
    
    Core principles:
    1. Raw Verbatim: record.raw_text = original conversation, no summarization
    2. Hash chain: each record contains previous record's hash (for integrity)
    3. Palace index: wing → hall → room → closet four-level spatial index
    4. Timeline retrieval: search by day/week/month/year
    
    Architecture:
      PalaceEngine
        ├── rooms: Dict[str, MemoryRoom]     # room_id → room
        ├── wing_index: Dict[PalaceWing, List[room_id]]
        ├── date_index: Dict[str, List[Tuple[str, str]]]  # date → [(room_id, record_id)]
        └── storage: Markdown file system (configurable path)
    """

    def __init__(
        self,
        palace_path: str = "~/.memory-palace",
        max_records_per_room: int = 10000,
    ):
        self.palace_path = Path(os.path.expanduser(palace_path))
        self.max_records_per_room = max_records_per_room

        # In-memory indexes
        self.rooms: Dict[str, MemoryRoom] = {}
        self.wing_index: Dict[PalaceWing, List[str]] = defaultdict(list)
        self.date_index: Dict[str, List[Tuple[str, str]]] = defaultdict(list)
        self._current_hash: Optional[str] = None  # Hash chain head

        self._ensure_structure()
        self._load_index()

    def _ensure_structure(self):
        """Ensure Palace directory structure."""
        for wing in PalaceWing:
            wing_dir = self.palace_path / wing.value
            wing_dir.mkdir(parents=True, exist_ok=True)
            idx_file = wing_dir / "index.json"
            if not idx_file.exists():
                idx_file.write_text(json.dumps({"rooms": []}, ensure_ascii=False))

    def _load_index(self):
        """Load index from disk."""
        self.rooms.clear()
        self.wing_index.clear()
        self.date_index.clear()

        for wing in PalaceWing:
            wing_dir = self.palace_path / wing.value
            if not wing_dir.exists():
                continue
            for room_dir in wing_dir.iterdir():
                if not room_dir.is_dir():
                    continue
                meta_file = room_dir / "meta.json"
                if not meta_file.exists():
                    continue
                try:
                    meta = json.loads(meta_file.read_text(encoding="utf-8"))
                    room = MemoryRoom(
                        room_id=meta["room_id"],
                        name=meta["name"],
                        wing=PalaceWing(wing.value),
                        hall=meta.get("hall", "general"),
                        closet=meta.get("closet", ""),
                        description=meta.get("description", ""),
                    )
                    room.tags = set(meta.get("tags", []))
                    self.rooms[room.room_id] = room
                    self.wing_index[PalaceWing(wing.value)].append(room.room_id)
                except Exception as e:
                    logger.warning(f"Failed to load room {room_dir}: {e}")

        # Load hash chain head
        chain_file = self.palace_path / ".chain_head"
        if chain_file.exists():
            self._current_hash = chain_file.read_text().strip()

    # ── store(): Write memory (Raw Verbatim) ─────────────────────────

    def store(
        self,
        raw_text: str,
        room_id: str,
        wing: PalaceWing,
        hall: str = "general",
        closet: str = "",
        speaker: str = "human",
        tags: List[str] = None,
        sources: List[str] = None,
        metadata: Dict[str, Any] = None,
    ) -> MemoryRecord:
        """
        Store memory (Raw Verbatim).
        
        - Raw Verbatim: raw_text = original conversation text, unfiltered
        - Hash chain: each record contains previous record's hash
        - Auto wing classification: based on wing parameter
        """
        tags = tags or []
        sources = sources or []
        metadata = metadata or {}

        # Create record with hash chain
        current_hash = MemoryRecord.compute_hash(raw_text, self._current_hash)
        record = MemoryRecord(
            record_id=hashlib.sha256(
                f"{raw_text}{datetime.now()}".encode()
            ).hexdigest()[:16],
            room_id=room_id,
            raw_text=raw_text,
            speaker=speaker,
            timestamp=datetime.now(),
            hash_chain=current_hash,
            metadata={**metadata, "wing": wing.value, "hall": hall, "closet": closet},
            tags=set(tags),
            sources=sources,
        )

        # Update hash chain head
        self._current_hash = current_hash

        # Get or create room
        if room_id not in self.rooms:
            room = MemoryRoom(
                room_id=room_id, 
                name=room_id, 
                wing=wing, 
                hall=hall, 
                closet=closet
            )
            self.rooms[room_id] = room
            self.wing_index[wing].append(room_id)
            self._save_room_meta(room)

        room = self.rooms[room_id]
        room.add(record)

        # Append to file (Raw Verbatim)
        self._append_to_file(wing, room_id, record)

        # Update date index
        date_key = record.timestamp.strftime("%Y-%m-%d")
        self.date_index[date_key].append((room_id, record.record_id))

        # Save hash chain file
        (self.palace_path / ".chain_head").write_text(record.hash_chain or "GENESIS")

        logger.info(f"Palace store: {record.record_id} in {room_id} (wing={wing.value})")
        return record

    def _append_to_file(
        self, 
        wing: PalaceWing, 
        room_id: str, 
        record: MemoryRecord
    ):
        """Append record to Markdown file (Raw Verbatim)."""
        room_dir = self.palace_path / wing.value / room_id
        room_dir.mkdir(parents=True, exist_ok=True)

        record_file = room_dir / f"{record.record_id}.md"
        content = (
            f"---\n"
            f"record_id: {record.record_id}\n"
            f"room_id: {record.room_id}\n"
            f"speaker: {record.speaker}\n"
            f"timestamp: {record.timestamp.isoformat()}\n"
            f"hash_chain: {record.hash_chain}\n"
            f"tags: [{', '.join(record.tags)}]\n"
            f"sources: [{', '.join(record.sources)}]\n"
            f"---\n\n"
            f"{record.raw_text}\n"
        )
        record_file.write_text(content, encoding="utf-8")

    def _save_room_meta(self, room: MemoryRoom):
        """Save room metadata."""
        room_dir = self.palace_path / room.wing.value / room.room_id
        room_dir.mkdir(parents=True, exist_ok=True)
        meta = {
            "room_id": room.room_id,
            "name": room.name,
            "wing": room.wing.value,
            "hall": room.hall,
            "closet": room.closet,
            "description": room.description,
            "tags": list(room.tags),
            "created_at": room.created_at.isoformat(),
        }
        (room_dir / "meta.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2)
        )

    # ── retrieve(): Retrieve memories ─────────────────────────────────

    def retrieve(
        self,
        query: str,
        wing: Optional[PalaceWing] = None,
        room_id: Optional[str] = None,
        since: datetime = None,
        until: datetime = None,
        max_records: int = 10,
    ) -> List[Tuple[MemoryRecord, float, str]]:
        """
        Retrieve memories (keyword-based, non-vector).
        
        Returns:
            [(record, score, room_id)]
        """
        rooms_to_search = []
        if room_id:
            rooms_to_search = [self.rooms[room_id]] if room_id in self.rooms else []
        elif wing:
            for rid in self.wing_index.get(wing, []):
                if rid in self.rooms:
                    rooms_to_search.append(self.rooms[rid])
        else:
            rooms_to_search = list(self.rooms.values())

        results: List[Tuple[MemoryRecord, float, str]] = []
        for room in rooms_to_search:
            room_results = room.search(query)
            for record, score in room_results:
                if since and record.timestamp < since:
                    continue
                if until and record.timestamp > until:
                    continue
                results.append((record, score, room.room_id))

        return sorted(results, key=lambda x: -x[1])[:max_records]

    def retrieve_timeline(
        self,
        since: datetime,
        until: datetime = None,
        wing: Optional[PalaceWing] = None,
    ) -> List[MemoryRecord]:
        """
        Timeline retrieval - get all memories within a time period.
        """
        if until is None:
            until = datetime.now()

        results = []
        current = since
        while current <= until:
            date_key = current.strftime("%Y-%m-%d")
            for room_id, record_id in self.date_index.get(date_key, []):
                if room_id in self.rooms:
                    room = self.rooms[room_id]
                    if wing and room.wing != wing:
                        continue
                    for record in room.records:
                        if record.record_id == record_id:
                            if since <= record.timestamp <= until:
                                results.append(record)
            current += timedelta(days=1)

        return sorted(results, key=lambda r: r.timestamp)

    # ── walk(): Memory palace navigation ─────────────────────────────

    def walk(
        self,
        start_room_id: Optional[str] = None,
        max_hops: int = 3,
    ) -> List[MemoryRoom]:
        """
        Memory Palace Walk - navigate through associated rooms.
        
        Simulates the spatial navigation of the ancient Greek memory technique.
        """
        if start_room_id and start_room_id not in self.rooms:
            return []

        visited: Set[str] = set()
        queue = [start_room_id] if start_room_id else list(self.rooms.keys())[:1]
        result: List[MemoryRoom] = []

        while queue and len(result) < max_hops * 3:
            room_id = queue.pop(0)
            if room_id in visited:
                continue
            visited.add(room_id)
            room = self.rooms[room_id]
            result.append(room)

            # Find other rooms in the same wing
            wing_rooms = self.wing_index.get(room.wing, [])
            for rid in wing_rooms[:2]:
                if rid not in visited:
                    queue.append(rid)

        return result

    # ── stats(): Statistics ─────────────────────────────────────────

    def stats(self) -> Dict[str, Any]:
        """Return Palace statistics."""
        wing_counts = defaultdict(int)
        total_records = 0
        oldest = None
        newest = None

        for room in self.rooms.values():
            wing_counts[room.wing.value] += len(room.records)
            total_records += len(room.records)
            if room.records:
                first = room.records[0]
                last = room.records[-1]
                if oldest is None or first.timestamp < oldest:
                    oldest = first.timestamp
                if newest is None or last.timestamp > newest:
                    newest = last.timestamp

        return {
            "total_rooms": len(self.rooms),
            "total_records": total_records,
            "by_wing": dict(wing_counts),
            "oldest_record": oldest.isoformat() if oldest else None,
            "newest_record": newest.isoformat() if newest else None,
            "chain_head": self._current_hash,
            "palace_path": str(self.palace_path),
        }


# ═══════════════════════════════════════════════════════════════════
# PalaceMemory Facade (Unified Interface)
# ═══════════════════════════════════════════════════════════════════

class PalaceMemory:
    """
    Memory Palace Facade - unified interface for memory operations.
    
    Workflow:
    1. User conversation → Palace.store() (Raw Verbatim)
    2. Palace.retrieve() → Search memories
    3. Timeline retrieval → Get memories in time range
    """

    def __init__(
        self,
        palace_path: str = "~/.memory-palace",
    ):
        self.palace = PalaceEngine(palace_path=palace_path)

    def remember(
        self,
        conversation: str,
        wing: PalaceWing = PalaceWing.GENERAL,
        room_id: str = None,
        speaker: str = "human",
    ) -> MemoryRecord:
        """Store a memory."""
        room_id = room_id or f"room-{datetime.now().strftime('%Y%m%d')}"
        return self.palace.store(
            raw_text=conversation,
            room_id=room_id,
            wing=wing,
            speaker=speaker,
        )

    def recall(
        self,
        query: str,
        wing: PalaceWing = None,
        since_days: int = 30,
    ) -> List[Tuple[MemoryRecord, float]]:
        """Retrieve memories."""
        since = datetime.now() - timedelta(days=since_days)
        results = self.palace.retrieve(
            query=query,
            wing=wing,
            since=since,
            max_records=10,
        )
        return [(r, s) for r, s, _ in results]

    def timeline(
        self,
        days: int = 7,
        wing: PalaceWing = None,
    ) -> List[MemoryRecord]:
        """Get memories in time range."""
        until = datetime.now()
        since = until - timedelta(days=days)
        return self.palace.retrieve_timeline(since=since, until=until, wing=wing)

    def stats(self) -> Dict[str, Any]:
        """Get palace statistics."""
        return self.palace.stats()
