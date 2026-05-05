# AIUCE Memory Palace

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Raw Verbatim memory storage based on the ancient Greek memory technique.

---

## Overview | 概述

Memory Palace implements a spatial memory system where information is organized into hierarchical categories (Wings → Halls → Rooms → Closets). It follows the **Raw Verbatim** philosophy: store complete original conversations without summarization or filtering.

Memory Palace 实现了一个空间记忆系统，信息被组织为层级结构（厅→走廊→房间→壁橱）。它遵循**Raw Verbatim**理念：完整存储原始对话，不做摘要或过滤。

---

## Core Principles | 核心原则

1. **Raw Verbatim** — Original text is stored intact, no summarization
2. **Spatial Indexing** — Organize memories by context (Wing → Hall → Room)
3. **Timeline Retrieval** — Search memories by date ranges
4. **Hash Chain Integrity** — Optional hash chain for record verification

---

## Palace Wings | 记忆宫殿分区

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

---

## Quick Start | 快速开始

```bash
pip install aiuce-memory-palace
```

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

---

## API | API

### PalaceMemory

- `remember(conversation, wing, room_id, speaker)` — Store a memory
- `recall(query, wing, since_days)` — Search memories
- `timeline(days, wing)` — Get memories in time range
- `stats()` — Get palace statistics

### PalaceEngine (Advanced)

- `store(raw_text, room_id, wing, hall, closet, ...)` — Direct storage
- `retrieve(query, wing, room_id, since, until)` — Direct retrieval
- `walk(start_room_id, max_hops)` — Navigate palace rooms

---

## License | 许可证

MIT License — Copyright © 2026 Bill Gao
