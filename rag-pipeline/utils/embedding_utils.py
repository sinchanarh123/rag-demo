from sentence_transformers import SentenceTransformer


class EmbeddingUtils:
    _model = None

    def __init__(self):
        if EmbeddingUtils._model is None:
            EmbeddingUtils._model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        self.model = EmbeddingUtils._model

    def create_embeddings(self, text_chunks):
        print("chunks received for embedding:", (text_chunks))
        embeddings = self.model.encode(text_chunks)

        print("*******")
        print(len(embeddings))
        print(len(text_chunks))
        return embeddings

    def create_query_embedding(self, query_text):
        embedding = self.model.encode(query_text)
        return embedding
