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


    def _recursive_split(self, text: str, max_size: int) -> List[str]:
        """
        Recursively split text by big to small separators until all chunks are <= max_size.
        Order: paragraphs (\n\n), lines (\n), sentences, spaces.
        """
        if len(text) <= max_size:
            return [text]
        # Try paragraphs
        paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        if len(paras) > 1:
            chunks = []
            buf = ""
            for para in paras:
                if len(buf) + len(para) + 2 <= max_size:
                    buf = buf + ("\n\n" if buf else "") + para
                else:
                    if buf:
                        chunks.extend(self._recursive_split(buf, max_size))
                    buf = para
            if buf:
                chunks.extend(self._recursive_split(buf, max_size))
            return chunks
        # Try lines
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        if len(lines) > 1:
            chunks = []
            buf = ""
            for line in lines:
                if len(buf) + len(line) + 1 <= max_size:
                    buf = buf + ("\n" if buf else "") + line
                else:
                    if buf:
                        chunks.extend(self._recursive_split(buf, max_size))
                    buf = line
            if buf:
                chunks.extend(self._recursive_split(buf, max_size))
            return chunks
        # Try sentences
        sents = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
        if len(sents) > 1:
            chunks = []
            buf = ""
            for sent in sents:
                if len(buf) + len(sent) + 1 <= max_size:
                    buf = buf + (" " if buf else "") + sent
                else:
                    if buf:
                        chunks.extend(self._recursive_split(buf, max_size))
                    buf = sent
            if buf:
                chunks.extend(self._recursive_split(buf, max_size))
            return chunks
        # Finally, split by spaces if still too large
        if len(text) > max_size:
            words = text.split()
            chunks = []
            buf = ""
            for word in words:
                if len(buf) + len(word) + 1 <= max_size:
                    buf = buf + (" " if buf else "") + word
                else:
                    if buf:
                        chunks.append(buf)
                    buf = word
            if buf:
                chunks.append(buf)
            return chunks
        return [text]

    def create_chunks(self, document: Dict) -> List[Dict]:
        text = document["text"]
        source = document["metadata"]["source"]

        # Use recursive character splitter
        base_chunks = self._recursive_split(text, self.chunk_size)

        chunks = []
        prev_tail = ""
        for chunk_id, chunk_text in enumerate(base_chunks):
            if self.chunk_overlap > 0 and prev_tail:
                chunk_text = prev_tail + "\n\n" + chunk_text
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
        return chunks