"""TF-IDF based text retrieval over uploaded document chunks.

Uses jieba for Chinese tokenization and scikit-learn's TfidfVectorizer.
The index is rebuilt lazily when new chunks are added. Fully offline.
"""
import threading
from typing import Dict, List

import jieba
from sklearn.feature_extraction.text import TfidfVectorizer

from ..models import DocumentChunk

jieba.setLogLevel(60)  # silence jieba build info


class _VectorStore:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._last_chunk_id = None
        self._vectorizer = None
        self._matrix = None
        self._chunks: List[dict] = []

    def _tokenize(self, text: str) -> str:
        return " ".join(jieba.cut(text))

    def _rebuild(self, db) -> None:
        rows = db.query(DocumentChunk).all()
        max_id = max((r.id for r in rows), default=0)
        if self._last_chunk_id is not None and max_id == self._last_chunk_id:
            return
        corpus = [r.content for r in rows]
        if not corpus:
            self._vectorizer = None
            self._matrix = None
            self._chunks = []
            self._last_chunk_id = max_id
            return
        self._vectorizer = TfidfVectorizer(
            tokenizer=lambda t: jieba.lcut(t),
            token_pattern=None,
            lowercase=False,
            sublinear_tf=True,
        )
        self._matrix = self._vectorizer.fit_transform(corpus)
        self._chunks = [
            {"id": r.id, "dataset_id": r.dataset_id, "content": r.content}
            for r in rows
        ]
        self._last_chunk_id = max_id

    def search(self, db, query: str, top_k: int = 5) -> List[Dict]:
        with self._lock:
            self._rebuild(db)
            if self._matrix is None or not query.strip():
                return []
            q_vec = self._vectorizer.transform([self._tokenize(query)])
            from sklearn.metrics.pairwise import cosine_similarity
            scores = cosine_similarity(q_vec, self._matrix)[0]
            top = scores.argsort()[::-1][:top_k]
            results = []
            for idx in top:
                score = float(scores[idx])
                if score <= 0.0:
                    continue
                item = dict(self._chunks[idx])
                item["score"] = round(score, 4)
                results.append(item)
            return results


vector_store = _VectorStore()
