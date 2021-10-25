from pydantic import BaseModel, HttpUrl
from typing import List, Optional


class SaveArticle(BaseModel):
    title: str
    article_data: dict
    published: bool = False
    hosts: List[HttpUrl]
    tags: Optional[str] = None
    edit: bool = False
