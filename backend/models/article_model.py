from pydantic import BaseModel
from typing import Optional

class Article(BaseModel):
    id: Optional[str] = None
    title: str
    source: str
    content: str
    tag: str