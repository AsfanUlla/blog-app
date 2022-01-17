from pydantic import BaseModel, EmailStr, HttpUrl
from common.views import PyObjectId
from typing import Dict


class AddUserSchema(BaseModel):
    full_name: str
    email: EmailStr
    passwd: str
    is_verified: bool = False
    is_editor: bool = False
    is_su_admin: bool =False
    is_diabled: bool = False
    social: Dict[str, HttpUrl] = {}


class UserLoginSchema(BaseModel):
    user_email: EmailStr
    passwd: str


class AddHostSchema(BaseModel):
    host: HttpUrl
    enabled: bool = False

class Subs(BaseModel):
    email: EmailStr


class ContactSchema(BaseModel):
    name: str
    email: EmailStr
    message: str
