from pydantic import BaseModel, Field
from typing import Optional


class BulkCreateByCount(BaseModel):
    count: int = Field(..., gt=0, le=500, example=50)
    profile: Optional[str] = Field(default="default", example="1hr")
    username_prefix: Optional[str] = Field(default="user", example="v")
    password_length: Optional[int] = Field(default=6, ge=4, le=12)
