from fastapi import APIRouter, HTTPException
from models.explain_request import ExplainRequest
from agents.context_explainer import context_explainer_handle_article

router = APIRouter()



@router.post('/explain')
async def explain_article(request: ExplainRequest):
    
    selected_text = await context_explainer_handle_article(request.text)

    explanation = {
        "sentence": request.text,
        "plain_explanation": selected_text
    }
    return {'explanation': explanation}
