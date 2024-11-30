from pydantic import BaseModel
from typing import Optional


class UserBaseSchema(BaseModel):
    id: int
    username: Optional[str] = None
    first_name: str
    last_name: Optional[str] = None
    lang: str = "en"
    last_alerted_rate: Optional[float] = None
    notify: bool = True


class UserSchema(UserBaseSchema):
    pass


class UserCreateSchema(UserBaseSchema):
    pass


class UserUpdateSchema(BaseModel):
    id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    lang: Optional[str] = None
    notify: Optional[bool] = None
