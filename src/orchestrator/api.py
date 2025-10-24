# type: ignore
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import logging

from orchestrator.graph import Orchestrator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="LangGraph Orchestrator")
orth = Orchestrator()

class Query(BaseModel):
    text: str

@app.post("/query")
async def query(q: Query):
    try:
        logger.info(f"Processing query: {q.text}")
        result = await orch.run(q.text)
        logger.info(f"Query result: {result}")
        return {"ok": True, "result": result}
    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10120)