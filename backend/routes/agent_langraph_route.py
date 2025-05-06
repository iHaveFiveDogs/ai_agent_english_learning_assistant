from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from ai_service.agents.agent_langraph import agent_langraph_answer
import asyncio

router = APIRouter()

@router.post("/agent_langraph_answer")
async def agent_langraph_endpoint(request: Request):
    data = await request.json()
    # Call the async function from agent_langraph
    answer = await agent_langraph_answer(data)
    return JSONResponse(content=answer)
