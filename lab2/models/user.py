from pydantic import BaseModel


class User(BaseModel):
    id: int
    login: str
    name: str
    surname: str
    password: str


class UpdateUser(BaseModel):
    login: str
    name: str
    surname: str
    password: str