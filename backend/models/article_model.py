from pydantic import BaseModel

class Article(BaseModel):
    title: str
    source: str
    content: str
    tag: str