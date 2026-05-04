from fastapi import FastAPI
from pydantic import BaseModel
from app.services.llm_service import get_fastest_response

app = FastAPI()

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def home():
    return {"message": "AI LLM System Running "}

@app.post("/chat")
async def chat(req: ChatRequest):
    response = await get_fastest_response(req.message)
    return {"response": response}