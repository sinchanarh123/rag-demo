from utils.text_utils import TextUtils
from utils.embedding_utils import EmbeddingUtils
from db.crud import CRUD

class IngestionService:
    def ingest_data(self, data, source_name="uploaded_file"):
        # Logic to ingest data
        text = TextUtils.pdf_to_text(data)
        chunks = TextUtils.get_chunks(text)
        embeddings = EmbeddingUtils().create_embeddings(chunks)
        # Logic to store embeddings

        crud = CRUD()

        for i in range(len(embeddings)):
            embedding = embeddings[i]
            print(len(embedding))
            chunk = chunks[i]
            chunk_id = i
            print("Embedding for chunk", chunk_id, ":", embedding)
            print("Chunk text:", chunk)
            crud.create(embedding, chunk, chunk_id, source_name)

        return len(chunks)
