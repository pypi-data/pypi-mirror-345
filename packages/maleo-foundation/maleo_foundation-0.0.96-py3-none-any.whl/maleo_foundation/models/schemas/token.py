from __future__ import annotations
from pydantic import BaseModel, Field
from maleo_foundation.types import BaseTypes

class BaseTokenSchemas:
    class Key(BaseModel):
        key:str = Field(..., description="Key")

    class Password(BaseModel):
        password:BaseTypes.OptionalString = Field(None, min_length=32, max_length=1024, description="password")

    class Token(BaseModel):
        token:str = Field(..., description="Token")

    class ExpIn(BaseModel):
        exp_in:int = Field(5, ge=5, description="Expires in (integer, minutes)")