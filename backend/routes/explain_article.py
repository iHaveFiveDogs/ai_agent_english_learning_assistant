from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from models.explain_request import ExplainRequest
from ai_service.intelligence.chosen_text_explainer import context_explainer_handle_article

router = APIRouter()



@router.post('/explain')
async def explain_article(request: ExplainRequest):
    
    ai_explanation = await context_explainer_handle_article(request.text)
    
    if not ai_explanation or "explanation" not in ai_explanation:
        return JSONResponse(content={"error": "Failed to generate explanation."}, status_code=500)
    explanation = ai_explanation["explanation"]

    return JSONResponse(content={"explanation": explanation})
