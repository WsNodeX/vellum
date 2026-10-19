"""检索入口：把笔记建索引并返回带摘要的命中结果。"""

from typing import Dict, List

from .index import BM25
from .models import Note, Store


def build_index(notes: List[Note]) -> BM25:
    idx = BM25()
    for n in notes:
        # 标题加权（重复一次）、标签纳入检索
        idx.add(n.id, f"{n.title} {n.title} {' '.join(n.tags)} {n.content}")
    idx.build()
    return idx


def search(store: Store, query: str, top_k: int = 10) -> List[Dict]:
    notes = store.all()
    if not notes:
        return []
    idx = build_index(notes)
    hits = idx.search(query, top_k=top_k)
    note_map = {n.id: n for n in notes}
    results: List[Dict] = []
    for nid, score in hits:
        n = note_map.get(nid)
        if n:
            results.append(
                {
                    "id": n.id,
                    "title": n.title,
                    "tags": n.tags,
                    "score": round(score, 4),
                    "snippet": _snippet(n.content, query),
                }
            )
    return results


def _snippet(content: str, query: str, length: int = 120) -> str:
    low = content.lower()
    pos = -1
    for t in query.lower().split():
        p = low.find(t)
        if p != -1:
            pos = p
            break
    if pos == -1:
        return content[:length] + ("…" if len(content) > length else "")
    start = max(0, pos - 40)
    end = min(len(content), start + length)
    return ("…" if start > 0 else "") + content[start:end] + ("…" if end < len(content) else "")
