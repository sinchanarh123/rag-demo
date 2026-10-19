# PDF Query Service
FastAPI microservice that turns uploaded PDFs into chunks, stores embeddings in Qdrant, and lets you ask directed questions with a strict RAG workflow.

## Features
- **PDF ingestion** – `ingestion.py` uses `pdfplumber` → `langchain` splitter → `sentence-transformers` to convert documents into overlapping chunks and embeddings.
- **Vector storage** – `db/crud.py` persists embeddings with metadata (chunk ID, source name) into a local Qdrant collection.
- **Semantic query** – `query.py` compares query embeddings against Qdrant, builds a citation-aware context and hits a local Llama 3.1:8b inference server for the final response.
- **FastAPI interface** – `main.py` exposes `/ingest` and `/query` for easy automation or integration with other services.

## Architecture

```
PDF binary → FastAPI `/ingest`
                   └─> TextUtils  → chunk → EmbeddingUtils → CRUD → Qdrant

Query JSON → FastAPI `/query` → EmbeddingUtils → CRUD search → QueryService → Llama3.1 server → response
```

## Getting started

### Prerequisites
- Python 3.9+ (a virtual environment lives under `venv/` in this repo)
- Qdrant running on `http://localhost:6333` (e.g., `docker run -p 6333:6333 qdrant/qdrant`)
- A Llama3.1 instance (or other compatible API) listening on `http://localhost:11434/api/generate`

### Install dependencies
```bash
python -m pip install fastapi uvicorn qdrant-client pdfplumber langchain sentence-transformers requests
```

### Run the API
```bash
uvicorn main:app --reload
```

## API

### `POST /ingest`
- **Body:** multipart form with a `file` field containing a PDF.
- **Behavior:** extracts text, splits into `450`-char chunks with `75`-char overlap, creates embeddings, and stores each chunk in Qdrant with metadata.
- **Response:** number of ingested chunks.

```bash
curl -X POST http://localhost:8000/ingest -F \"file=@./docs/spec.pdf\"
```

### `POST /query`
- **Body:** JSON `{ \"query\": \"Your question\", \"top_k\": 3 }`
- **Behavior:** embeds the prompt, retrieves the top `top_k` matches, and asks the Llama3.1 server to answer using only that context.
- **Response:** includes the model’s answer, citation info, and the raw matches returned by Qdrant.

```bash
curl -X POST http://localhost:8000/query -H \"Content-Type: application/json\" -d '{\"query\":\"What is this PDF about?\",\"top_k\":4}'
```

## Implementation notes
- `TextUtils.get_chunks` uses `CharacterTextSplitter` with whitespace, so PDFs with complex layout may need custom splitting logic.
- `EmbeddingUtils` caches the `sentence-transformers/all-MiniLM-L6-v2` model in memory for reuse.
- `CRUD` always targets the `test_collection` vector store. Change `collection_name` in `db/crud.py` if you need multiple datasets.
- Query service wraps the retrieved context in numbered citations and enforces a strict “answer from the provided context” policy before calling the Llama server.

## Extending the stack
- Add authentication or file type validation in `main.py` if you expose ingestion publicly.
- Swap the model behind `EmbeddingUtils` or replace the Llama endpoint URL with another model-as-a-service provider (just keep the prompt structure).
- Persist metadata beyond `source_name`/`chunk_id` (e.g., page numbers) by extending the payload.
- Refactor ingestion/query services into clearer layers (e.g., split validation, embedding, storage) so new logic plugs in cleanly.
- Add structured exception handling and logging around file reads, model calls, and Qdrant interactions to make failures easier to debug.

## Next steps
- Run ingestion against a representative document, then query for fact-based answers to verify the citation workflow.
- Monitor the Qdrant dashboard (if enabled) to ensure your collection stays within resource limits.
