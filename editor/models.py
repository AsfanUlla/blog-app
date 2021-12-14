from pydantic import BaseModel, HttpUrl, validator
from typing import List, Optional
from common.views import PyObjectId
from fastapi import HTTPException, status

class SaveArticle(BaseModel):
    title: str = ""
    article_data: dict = {}
    published: bool = False
    hosts: List[str] = []
    tags: Optional[str] = None
    edit: bool = False
    article_id: Optional[PyObjectId] = None

class SaveArticleV2(BaseModel):
    title: str = ""
    article_data: dict = {}
    hosts: List[str] = []
    tags: Optional[str] = None
    is_suspended: bool = False
    article_id: Optional[PyObjectId] = None
    fsave: bool = False

    @validator('fsave')
    @classmethod
    def fsave_check(cls, v, values):
        if v:
            title = parse(values["title"], fuzzy=False)
            hosts = parse(values["hosts"], fuzzy=False)
            if len(title.strip()) == 0 or len(hosts) == 0:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Title or Host field cannot be empty")

class PubOrUn(BaseModel):
    article_id: Optional[PyObjectId] = None
    published: bool = False

class Discard(BaseModel):
    article_id: PyObjectId
