
from pydantic import BaseModel

class ExplainRequest(BaseModel):
    text: str