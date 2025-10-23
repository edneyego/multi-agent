# type: ignore
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

from orchestrator.graph import Orchestrator

app = FastAPI(title="LangGraph Orchestrator")
orch = Orchestrator()

class Query(BaseModel):
    text: str

@app.post("/query")
async def query(q: Query):
    result = await orch.run(q.text)
    return {"ok": True, "result": result}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10120)
