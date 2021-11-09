from fastapi import HTTPException, status, Header
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
from config import Config
from common.db import collections
from common.views import MongoInterface, RediectException, MLStripper
from bson import ObjectId
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from slugify import slugify
from urllib.parse import urlparse


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"

templates = Jinja2Templates(directory="templates")

def jslug_filter(text):
    return slugify(text)

def pop1(alist):
    del alist[0]
    return alist

def jpath(url):
    return str(urlparse(url).path)[1:]

def mil_date(time):
    date = datetime.fromtimestamp(time/1000.0).date().isoformat()
    return date

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

templates.env.trim_blocks = True
templates.env.lstrip_blocks = True
templates.env.filters['jslug'] = jslug_filter
templates.env.filters['pop1'] = pop1
templates.env.filters['jpath'] = jpath
templates.env.filters['mdate'] = mil_date
templates.env.filters['stag'] = strip_tags


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def create_access_token(data: dict, expires_delta: Optional[timedelta] = None, key: str = Config.JWT_SECRET_KEY):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, key, algorithm=ALGORITHM)
    return encoded_jwt


async def verify_token(request: Request):
    token = request.session.get('token')
    if not token:
        raise RediectException(path="/admin/login", status_code=status.HTTP_302_FOUND)
    key: str = Config.JWT_SECRET_KEY
    try:
        payload = jwt.decode(token, key, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Illegal token")
        user = await MongoInterface.find_or_404(
            collections['users'],
            query=dict(
                _id=ObjectId(user_id),
                is_diabled=False
            ),
            exclude=dict(
                _id=False,
                cd=False
            ),
            error_message="Illegal token"
        )
    except JWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Illegal token")
    return user, payload
