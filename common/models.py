from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any


class SchemalessResponse(BaseModel):
    data: Dict = {}
    status_code: int = 200
    message: Optional[str] = "Request Processed"


class EmailSchema(BaseModel):
    sub: str
    email_to: List[EmailStr]
    body: Any
    template_name: str = None
