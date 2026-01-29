from dotenv import load_dotenv
import os
import sys

# Add the current directory to sys.path so that 'services' module can be found
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Load environment variables from the .env file in the same directory
load_dotenv(os.path.join(current_dir, ".env"))
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from services.agent import run_agent

app = FastAPI(title="tcrm_brain", description="AI Intelligence Layer for CRM")

class QueryRequest(BaseModel):
    query: str

@app.get("/")
def read_root():
    return {"message": "TCRM Brain is active. POST to /ask to interact with the agent."}

@app.post("/ask")
def ask_agent(request: QueryRequest):
    """
    Endpoint to process natural language queries.
    """
    try:
        response = run_agent(request.query)
        result = response.get("output", "No response generated.")
        return {"response": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
