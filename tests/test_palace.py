"""
Basic tests for Memory Palace.
"""

import pytest
import tempfile
import shutil
from datetime import datetime, timedelta

from aiuce_memory_palace import PalaceMemory, PalaceEngine, PalaceWing, MemoryRecord


class TestPalaceWing:
    """Test PalaceWing enum."""

    def test_wing_values(self):
        """Verify all wings have valid values."""
        assert PalaceWing.PEOPLE.value == "people"
        assert PalaceWing.PROJECTS.value == "projects"
        assert PalaceWing.LEARNING.value == "learning"
        assert PalaceWing.HEALTH.value == "health"
        assert PalaceWing.FINANCE.value == "finance"
        assert PalaceWing.LIFE.value == "life"
        assert PalaceWing.REFLECTION.value == "reflection"
        assert PalaceWing.GENERAL.value == "general"


class TestMemoryRecord:
    """Test MemoryRecord dataclass."""

    def test_create_record(self):
        """Create a basic memory record."""
        record = MemoryRecord(
            record_id="test-001",
            room_id="test-room",
            raw_text="Hello world",
            speaker="human",
        )
        assert record.record_id == "test-001"
        assert record.room_id == "test-room"
        assert record.raw_text == "Hello world"
        assert record.speaker == "human"
        assert record.timestamp is not None

    def test_compute_hash(self):
        """Test hash computation."""
        hash1 = MemoryRecord.compute_hash("test text", None)
        hash2 = MemoryRecord.compute_hash("test text", None)
        hash3 = MemoryRecord.compute_hash("different", None)
        
        assert hash1 == hash2  # Same input = same hash
        assert hash1 != hash3  # Different input = different hash
        assert len(hash1) == 16

    def test_verify_chain(self):
        """Test hash chain verification."""
        prev_record = MemoryRecord(
            record_id="prev",
            room_id="test",
            raw_text="previous text",
            hash_chain="abc123",
        )
        
        # Create new record with correct hash
        new_text = "new text"
        correct_hash = MemoryRecord.compute_hash(new_text, prev_record.hash_chain)
        new_record = MemoryRecord(
            record_id="new",
            room_id="test",
            raw_text=new_text,
            hash_chain=correct_hash,
        )
        
        assert new_record.verify_chain(prev_record) is True
        
        # Test with wrong hash
        wrong_record = MemoryRecord(
            record_id="new",
            room_id="test",
            raw_text=new_text,
            hash_chain="wronghash",
        )
        assert wrong_record.verify_chain(prev_record) is False


class TestPalaceEngine:
    """Test PalaceEngine core functionality."""

    @pytest.fixture
    def temp_palace(self):
        """Create temporary palace directory."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    def test_init(self, temp_palace):
        """Test engine initialization."""
        engine = PalaceEngine(palace_path=temp_palace)
        assert engine.palace_path.exists()
        assert len(engine.rooms) == 0

    def test_store_and_retrieve(self, temp_palace):
        """Test storing and retrieving memories."""
        engine = PalaceEngine(palace_path=temp_palace)
        
        # Store a memory
        record = engine.store(
            raw_text="This is a test conversation about Python.",
            room_id="test-room",
            wing=PalaceWing.LEARNING,
            speaker="human",
        )
        
        assert record.record_id is not None
        assert record.raw_text == "This is a test conversation about Python."
        assert record.room_id == "test-room"
        
        # Retrieve
        results = engine.retrieve(query="Python", max_records=5)
        assert len(results) > 0
        retrieved_record, score, room_id = results[0]
        assert "Python" in retrieved_record.raw_text

    def test_retrieve_by_wing(self, temp_palace):
        """Test retrieval filtered by wing."""
        engine = PalaceEngine(palace_path=temp_palace)
        
        # Store in different wings
        engine.store(
            raw_text="About health and wellness.",
            room_id="health-room",
            wing=PalaceWing.HEALTH,
        )
        engine.store(
            raw_text="About project deadlines.",
            room_id="project-room",
            wing=PalaceWing.PROJECTS,
        )
        
        # Filter by wing
        results = engine.retrieve(query="deadlines", wing=PalaceWing.PROJECTS)
        assert len(results) > 0
        assert results[0][2] == "project-room"

    def test_stats(self, temp_palace):
        """Test statistics."""
        engine = PalaceEngine(palace_path=temp_palace)
        
        engine.store(
            raw_text="Test 1",
            room_id="room1",
            wing=PalaceWing.GENERAL,
        )
        engine.store(
            raw_text="Test 2",
            room_id="room2",
            wing=PalaceWing.GENERAL,
        )
        
        stats = engine.stats()
        assert stats["total_rooms"] == 2
        assert stats["total_records"] == 2


class TestPalaceMemory:
    """Test PalaceMemory facade."""

    @pytest.fixture
    def temp_palace(self):
        """Create temporary palace directory."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    def test_remember(self, temp_palace):
        """Test remember method."""
        palace = PalaceMemory(palace_path=temp_palace)
        
        record = palace.remember(
            conversation="Let's discuss the project.",
            wing=PalaceWing.PROJECTS,
            room_id="project-alpha",
        )
        
        assert record.raw_text == "Let's discuss the project."
        assert record.metadata["wing"] == "projects"

    def test_recall(self, temp_palace):
        """Test recall method."""
        palace = PalaceMemory(palace_path=temp_palace)
        
        palace.remember(
            conversation="Python is a great programming language.",
            wing=PalaceWing.LEARNING,
            room_id="python-room",
        )
        
        results = palace.recall("Python", since_days=30)
        assert len(results) > 0

    def test_timeline(self, temp_palace):
        """Test timeline method."""
        palace = PalaceMemory(palace_path=temp_palace)
        
        palace.remember(
            conversation="Test memory",
            wing=PalaceWing.GENERAL,
        )
        
        timeline = palace.timeline(days=7)
        assert len(timeline) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
