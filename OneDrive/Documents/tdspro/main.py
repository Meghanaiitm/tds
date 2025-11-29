# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
# CHANGE: Import from src.agent instead of agent
from src.agent import solve_task 

app = FastAPI()

class RequestData(BaseModel):
    email: str
    secret: str
    url: str

@app.get("/")
def home():
    return {"status": "Agent is running"}

@app.post("/run")
def run_agent(data: RequestData):
    try:
        result = solve_task(data.url, data.email, data.secret)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))