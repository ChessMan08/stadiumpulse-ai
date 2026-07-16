from dataclasses import dataclass

import numpy as np


@dataclass
class Document:
    doc_id: str
    title: str
    text: str
    vector: np.ndarray


class VectorStore:
    def __init__(self) -> None:
        self._docs: list[Document] = []

    def add(self, doc_id: str, title: str, text: str, vector: list[float]) -> None:
        self._docs.append(Document(doc_id, title, text, np.array(vector, dtype=float)))

    def search(self, query_vector: list[float], k: int = 2) -> list[Document]:
        if not self._docs:
            return []
        q = np.array(query_vector, dtype=float)
        q_norm = np.linalg.norm(q) or 1.0
        scored: list[tuple[float, Document]] = []
        for doc in self._docs:
            d_norm = np.linalg.norm(doc.vector) or 1.0
            similarity = float(np.dot(q, doc.vector) / (q_norm * d_norm))
            scored.append((similarity, doc))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [doc for _, doc in scored[:k]]

    def __len__(self) -> int:
        return len(self._docs)
