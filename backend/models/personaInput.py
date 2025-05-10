from pydantic import BaseModel
# Define the structured input
class PersonaInput(BaseModel):
    query: str