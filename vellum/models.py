"""数据模型与基于单 JSON 文件的本地存储。"""

from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional


@dataclass
class Note:
    id: str
    title: str
    content: str
    tags: List[str] = field(default_factory=list)
    created_at: float = 0.0
    updated_at: float = 0.0

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict) -> "Note":
        return cls(
            id=d.get("id", uuid.uuid4().hex),
            title=d.get("title", ""),
            content=d.get("content", ""),
            tags=d.get("tags", []),
            created_at=d.get("created_at", 0.0),
            updated_at=d.get("updated_at", 0.0),
        )


class Store:
    """极简笔记存储：全部笔记存进一个 JSON 文件。"""

    def __init__(self, path: str):
        self.path = path
        self._notes: Dict[str, Note] = {}
        self.load()

    def load(self) -> None:
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._notes = {n["id"]: Note.from_dict(n) for n in data.get("notes", [])}
        else:
            self._notes = {}

    def save(self) -> None:
        os.makedirs(os.path.dirname(os.path.abspath(self.path)), exist_ok=True)
        data = {"notes": [n.to_dict() for n in self._notes.values()]}
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add(self, title: str, content: str, tags: Optional[List[str]] = None) -> Note:
        now = time.time()
        note = Note(
            id=uuid.uuid4().hex,
            title=title,
            content=content,
            tags=tags or [],
            created_at=now,
            updated_at=now,
        )
        self._notes[note.id] = note
        self.save()
        return note

    def get(self, note_id: str) -> Optional[Note]:
        return self._notes.get(note_id)

    def update(self, note_id: str, **fields) -> Optional[Note]:
        note = self._notes.get(note_id)
        if not note:
            return None
        for k, v in fields.items():
            if k in ("title", "content", "tags"):
                setattr(note, k, v)
        note.updated_at = time.time()
        self.save()
        return note

    def delete(self, note_id: str) -> bool:
        if note_id in self._notes:
            del self._notes[note_id]
            self.save()
            return True
        return False

    def all(self) -> List[Note]:
        return list(self._notes.values())

    def count(self) -> int:
        return len(self._notes)
