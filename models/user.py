from pydantic import BaseModel

class UserQuery(BaseModel):
    id_number: int
    messages: str