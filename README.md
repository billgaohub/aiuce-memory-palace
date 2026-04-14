# Memory Palace

Raw Verbatim memory storage based on the ancient Greek memory technique.

## Overview

Memory Palace implements a spatial memory system where information is organized into hierarchical categories (Wings → Halls → Rooms → Closets). It follows the **Raw Verbatim** philosophy: store complete original conversations without summarization or filtering.

## Core Principles

1. **Raw Verbatim**: Original text is stored intact, no summarization
2. **Spatial Indexing**: Organize memories by context (Wing → Hall → Room → Closet)
3. **Timeline Retrieval**: Search memories by date ranges
4. **Hash Chain Integrity**: Optional hash chain for record verification

## Installation

```bash
pip install aiuce-memory-palace
```

## Quick Start

```python
from aiuce_memory_palace import PalaceMemory, PalaceWing

# Initialize palace (stores in ~/.memory-palace by default)
palace = PalaceMemory()

# Store a memory
record = palace.remember(
    conversation="Discussed project timeline with the team today.",
    wing=PalaceWing.PROJECTS,
    room_id="project-alpha"
)

# Recall memories
results = palace.recall("project timeline", wing=PalaceWing.PROJECTS)
for record, score in results:
    print(f"[{score:.2f}] {record.raw_text}")

# Get timeline
recent = palace.timeline(days=7)
```

## Architecture

```
PalaceMemory (Facade)
  └── PalaceEngine (Core)
        ├── rooms: Dict[str, MemoryRoom]
        ├── wing_index: Dict[PalaceWing, List[room_id]]
        └── date_index: Dict[date, List[(room_id, record_id)]]
```

## Palace Wings

| Wing | Description |
|------|-------------|
| `PEOPLE` | Conversations with others |
| `PROJECTS` | Work/project related |
| `LEARNING` | Books/courses/research |
| `HEALTH` | Body/medical/fitness |
| `FINANCE` | Money/investments/taxes |
| `LIFE` | Daily/family/travel |
| `REFLECTION` | Decisions/experience/lessons |
| `GENERAL` | Uncategorized |

## API

### PalaceMemory

- `remember(conversation, wing, room_id, speaker)` - Store a memory
- `recall(query, wing, since_days)` - Search memories
- `timeline(days, wing)` - Get memories in time range
- `stats()` - Get palace statistics

### PalaceEngine (Advanced)

- `store(raw_text, room_id, wing, hall, closet, ...)` - Direct storage
- `retrieve(query, wing, room_id, since, until)` - Direct retrieval
- `retrieve_timeline(since, until, wing)` - Timeline access
- `walk(start_room_id, max_hops)` - Navigate palace rooms

## License

MIT License - Copyright 2026 Bill Gao
