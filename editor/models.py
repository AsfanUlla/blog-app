from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from common.views import PyObjectId


class SaveArticle(BaseModel):
    title: str = ""
    article_data: dict = {}
    published: bool = False
    hosts: List[HttpUrl] = []
    tags: Optional[str] = None
    edit: bool = False
    article_id: Optional[PyObjectId] = None


class Discard(BaseModel):
    article_id: PyObjectId
