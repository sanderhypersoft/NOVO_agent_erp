from fastapi import FastAPI, Request
import os
import sys

# Ajuste de path para que a função na pasta /api enxergue o root do projeto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pipeline_executor import PipelineExecutor
from agent_state import AgentState

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
    
    try:
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
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return {
            "error": "Internal Server Error during execution",
            "message": str(e),
            "traceback": error_details
        }
