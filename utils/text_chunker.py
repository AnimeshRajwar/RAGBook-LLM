from typing import List, Dict, Optional
import math
import re
from utils.config import EMBEDDING_MODEL_NAME
from .embedding_generator import EmbeddingGenerator


def _cosine_similarity(a: List[float], b: List[float]) -> float:
    denom_a = math.sqrt(sum(x * x for x in a))
    denom_b = math.sqrt(sum(x * x for x in b))
    if denom_a == 0 or denom_b == 0:
        return 0.0
    return sum(x * y for x, y in zip(a, b)) / (denom_a * denom_b)


class TextChunker:
    """Semantic chunker: groups paragraphs by semantic similarity.

    Strategy:
    - Split text into paragraphs (double-newline). If only one paragraph,
      fall back to a sentence-level split.
    - Compute embeddings for each paragraph.
    - Grow a chunk by adding consecutive paragraphs while the centroid
      similarity stays above a threshold and the character-length stays
      under `chunk_size`.
    - Optionally prepend a small character-overlap from the previous
      chunk to improve retrieval continuity.
    """

    def __init__(self, chunk_size: int, chunk_overlap: int, embedder: Optional[EmbeddingGenerator] = None, similarity_threshold: float = 0.72):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.similarity_threshold = similarity_threshold
        self.embedder = embedder or EmbeddingGenerator(EMBEDDING_MODEL_NAME)

    def _split_paragraphs(self, text: str) -> List[str]:
        paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        if len(paras) <= 1:
            paras = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
        return paras if paras else [text]

    def create_chunks(self, document: Dict) -> List[Dict]:
        text = document["text"]
        source = document["metadata"]["source"]

        paragraphs = self._split_paragraphs(text)

        para_embeddings = self.embedder.generate_embeddings(paragraphs)

        chunks = []
        i = 0
        chunk_id = 0
        prev_tail = ""

        while i < len(paragraphs):
            current_paras = [paragraphs[i]]
            current_embs = [para_embeddings[i]]
            current_text = paragraphs[i]

            j = i + 1
            while j < len(paragraphs):
                next_para = paragraphs[j]
                next_emb = para_embeddings[j]

                centroid = [sum(col) / len(col) for col in zip(*current_embs)]
                sim = _cosine_similarity(centroid, next_emb)

                if len(current_text) + 1 + len(next_para) > self.chunk_size:
                    break

                if sim >= self.similarity_threshold:
                    current_paras.append(next_para)
                    current_embs.append(next_emb)
                    current_text = current_text + "\n\n" + next_para
                    j += 1
                else:
                    break

            if self.chunk_overlap > 0 and prev_tail:
                chunk_text = prev_tail + "\n\n" + current_text
            else:
                chunk_text = current_text

            chunks.append({
                "id": f"{source}_chunk_{chunk_id}",
                "text": chunk_text,
                "metadata": {"source": source}
            })

            if self.chunk_overlap > 0:
                tail = chunk_text[-self.chunk_overlap:]
                prev_tail = tail
            else:
                prev_tail = ""

            chunk_id += 1
            i = j

        return chunks