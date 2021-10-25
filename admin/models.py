from pydantic import BaseModel, Field, EmailStr, HttpUrl


class AddUserSchema(BaseModel):
    full_name: str = Field(...)
    email: EmailStr = Field(...)
    passwd: str = Field(...)


class UserLoginSchema(BaseModel):
    user_email: EmailStr
    passwd: str


class AddHostSchema(BaseModel):
    host: HttpUrl
    enabled: bool = False
