from pydantic import BaseModel
from typing import Optional


class UserBaseSchema(BaseModel):
    id: int
    username: Optional[str] = None
    first_name: str
    last_name: Optional[str] = None
    lang: str = "en"
    gz_threshold: float = 14.0
    google_threshold: float = 14.0
    cbrf_threshold: float = 14.0
    gz_notify: bool = True
    google_notify: bool = True
    cbrf_notify: bool = True


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


class UserNotificationUpdateSchema(BaseModel):
    id: int
    gz_notify: Optional[bool] = None
    google_notify: Optional[bool] = None
    cbrf_notify: Optional[bool] = None


class UserThresholdUpdateSchema(BaseModel):
    id: int
    gz_threshold: Optional[float] = None
    google_threshold: Optional[float] = None
    cbrf_threshold: Optional[float] = None
