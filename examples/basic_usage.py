"""
Basic usage example for Memory Palace.

Demonstrates core functionality: storing and retrieving memories.
"""

import tempfile
import shutil
from aiuce_memory_palace import PalaceMemory, PalaceWing


def main():
    # Use temporary directory for demo
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Initialize palace
        palace = PalaceMemory(palace_path=temp_dir)
        print("Palace initialized\n")
        
        # ── Store memories ───────────────────────────────────────────
        
        print("=== Storing Memories ===\n")
        
        # Conversation about a project
        record1 = palace.remember(
            conversation="We need to finalize the Q2 roadmap by Friday. "
                        "The team has been working on the new authentication system.",
            wing=PalaceWing.PROJECTS,
            room_id="q2-roadmap",
            speaker="human",
        )
        print(f"Stored: {record1.record_id}")
        
        # Conversation about learning
        record2 = palace.remember(
            conversation="Reading 'Designing Data-Intensive Applications'. "
                        "Chapter 3 covers storage engines and indexing.",
            wing=PalaceWing.LEARNING,
            room_id="ddia-book",
            speaker="human",
        )
        print(f"Stored: {record2.record_id}")
        
        # Conversation about health
        record3 = palace.remember(
            conversation="Morning run: 5km in 25 minutes. "
                        "Feeling good, need to stretch more.",
            wing=PalaceWing.HEALTH,
            room_id="running-journal",
            speaker="human",
        )
        print(f"Stored: {record3.record_id}")
        
        print()
        
        # ── Retrieve memories ───────────────────────────────────────
        
        print("=== Retrieving Memories ===\n")
        
        # Search for project-related memories
        print("Search: 'roadmap' in PROJECTS wing")
        results = palace.recall(
            query="roadmap",
            wing=PalaceWing.PROJECTS,
            since_days=30,
        )
        for record, score in results:
            print(f"  [{score:.2f}] {record.raw_text[:60]}...")
        
        print()
        
        # Search across all wings
        print("Search: 'chapter' (all wings)")
        results = palace.recall(
            query="chapter",
            since_days=30,
        )
        for record, score in results:
            print(f"  [{score:.2f}] {record.raw_text[:60]}...")
        
        print()
        
        # ── Timeline ───────────────────────────────────────────────
        
        print("=== Timeline (last 7 days) ===\n")
        timeline = palace.timeline(days=7)
        for record in timeline:
            print(f"  [{record.timestamp.strftime('%Y-%m-%d %H:%M')}] "
                  f"[{record.metadata['wing']}] {record.raw_text[:50]}...")
        
        print()
        
        # ── Statistics ─────────────────────────────────────────────
        
        print("=== Palace Statistics ===\n")
        stats = palace.stats()
        print(f"  Total rooms: {stats['total_rooms']}")
        print(f"  Total records: {stats['total_records']}")
        print(f"  By wing: {stats['by_wing']}")
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)
        print("\n[Demo complete - temp directory cleaned up]")


if __name__ == "__main__":
    main()
