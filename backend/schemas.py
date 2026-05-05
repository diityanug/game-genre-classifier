from pydantic import BaseModel

class GameRequest(BaseModel):
    title: str
    description: str