from fastapi import FastAPI, Request
from pipeline_executor import PipelineExecutor
from agent_state import AgentState
import os

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "Hyper Agent is Running on Vercel", "version": "1.0-hybrid"}

@app.post("/ask")
async def ask(request: Request):
    data = await request.json()
    question = data.get("question")
    
    if not question:
        return {"error": "Question is required"}
    
    executor = PipelineExecutor()
    context = executor.run(question)
    
    return {
        "question": question,
        "sql": context.data.get("sql"),
        "state": context.state.name,
        "errors": context.errors,
        "warnings": context.data.get("rule_warnings", []),
        "confidence": context.data.get("confidence", 0.0)
    }
