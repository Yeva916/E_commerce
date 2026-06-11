
from pydantic import BaseModel


class InputCategory(BaseModel):
    name:str
    description:str|None=None

class CategoryResponse(BaseModel):
    id:int
    name:str
    description:str|None=None
    is_archived:bool

    class Config:
        from_attributes = True