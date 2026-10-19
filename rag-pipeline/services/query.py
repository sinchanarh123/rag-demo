import os

from utils.embedding_utils import EmbeddingUtils
from db.crud import CRUD
import requests




class QueryService:
    def __init__(self):
        self.embedding_utils = EmbeddingUtils()
        self.crud = CRUD()

    def _generate_answer(self, query, matches):
        context_blocks = []
        for idx, match in enumerate(matches, start=1):
            context_blocks.append(
                f"[{idx}] source={match.get('source_name')} chunk={match.get('chunk_id')} score={match.get('score'):.4f}\n{match.get('text', '')}"
            )
        context_text = "\n\n".join(context_blocks)


        system_prompt = (
            "You are a strict RAG assistant. Answer only from provided context. "
            "If context is insufficient, say you do not have enough information. "
            "Cite sources as [1], [2], etc."
        )
        user_prompt = f"Question:\n{query}\n\nContext:\n{context_text}"
        prompt = f"{system_prompt}\n\n{user_prompt}"
        r = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "llama3.1:8b", "prompt": prompt, "stream": False},
        timeout=120,
        )
        r.raise_for_status()
        return r.json()["response"]

    def query_data(self, query, top_k=3):
        query_embedding = self.embedding_utils.create_query_embedding(query)
        matches = self.crud.read(query_embedding, limit=top_k)

        if not matches:
            return {
                "answer": "I could not find relevant context in the vector database.",
                "citations": [],
                "matches": [],
            }

        citations = []
        for idx, match in enumerate(matches, start=1):
            citations.append(
                {
                    "ref": idx,
                    "source_name": match.get("source_name"),
                    "chunk_id": match.get("chunk_id"),
                    "score": match.get("score"),
                }
            )

        answer = self._generate_answer(query, matches)
        return {
            "answer": answer,
            "citations": citations,
            "matches": matches,
        }
