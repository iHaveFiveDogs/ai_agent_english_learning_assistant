from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from ai_service.agents.chat_agent_langraph_simple import agent_langraph_chat
from fastapi.responses import StreamingResponse

router = APIRouter()

@router.post("/agent_langraph_answer")
async def agent_langraph_endpoint(request: Request):
    data = await request.json()
    # Call the async function from agent_langraph
    answer = await agent_langraph_chat(data)
    return JSONResponse(content=answer)

