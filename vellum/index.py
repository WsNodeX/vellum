"""BM25 全文索引与中英混合分词。"""

import math
import re
from typing import Dict, List, Tuple

_CJK = re.compile(r"[一-鿿]")
_TOKEN_RE = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> List[str]:
    """小写化后：英文/数字按词切；中文按二元（bigram）切，避免单字误命中。

    例：「全文检索」→ 全文/文检/检索；「python 检索」→ python/检索。
    """
    text = (text or "").lower()
    tokens: List[str] = list(_TOKEN_RE.findall(text))
    cjk = [ch for ch in text if _CJK.match(ch)]
    for i in range(len(cjk) - 1):
        tokens.append(cjk[i] + cjk[i + 1])
    return tokens


class BM25:
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.doc_ids: List[str] = []
        self.docs: List[List[str]] = []
        self.doc_len: List[int] = []
        self.df: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.avg_len: float = 0.0

    def add(self, doc_id: str, text: str) -> None:
        toks = tokenize(text)
        self.doc_ids.append(doc_id)
        self.docs.append(toks)
        self.doc_len.append(len(toks))
        for t in set(toks):
            self.df[t] = self.df.get(t, 0) + 1

    def build(self) -> None:
        n = len(self.docs)
        self.avg_len = (sum(self.doc_len) / n) if n else 0.0
        for t, dft in self.df.items():
            self.idf[t] = math.log(1 + (n - dft + 0.5) / (dft + 0.5))

    def search(self, query: str, top_k: int = 10) -> List[Tuple[str, float]]:
        q_toks = tokenize(query)
        if not q_toks or not self.docs:
            return []
        scores: Dict[str, float] = {}
        for i, doc in enumerate(self.docs):
            dl = self.doc_len[i]
            tf_map: Dict[str, int] = {}
            for t in doc:
                tf_map[t] = tf_map.get(t, 0) + 1
            score = 0.0
            for qt in q_toks:
                idf = self.idf.get(qt)
                if not idf:
                    continue
                tf = tf_map.get(qt, 0)
                if tf == 0:
                    continue
                denom = tf + self.k1 * (1 - self.b + self.b * dl / (self.avg_len or 1))
                score += idf * (tf * (self.k1 + 1)) / denom
            if score > 0:
                scores[self.doc_ids[i]] = score
        return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
