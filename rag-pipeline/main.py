from pydantic import BaseModel
from fastapi import FastAPI, File, UploadFile
from services.ingestion import IngestionService
from services.query import QueryService

app = FastAPI()


class QueryRequest(BaseModel):
    query: str
    top_k: int = 3

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.post("/ingest")
async def ingest_data(file: UploadFile = File(...)):
    # Here you would add logic to process and store the data
    try:
        file_bytes = await file.read()
        ingested_chunks = IngestionService().ingest_data(file_bytes, source_name=file.filename or "uploaded_file")
    except Exception as e:
        return {"status": "Error", "message": str(e)}   

    return {"status": "Data ingested successfully", "chunks_ingested": ingested_chunks}

@app.post("/query")
def query_data(req: QueryRequest):
    print("Received query:", req.query)
    resp = QueryService().query_data(req.query, top_k=req.top_k)
    return {"status": "Query processed successfully", "response": resp}
