from typing import Any

from pydantic import BaseModel #, Field
# import uuid


class MethodCall(BaseModel):
    service: str
    method: str
    # fancy_key: str = Field(default_factory=lambda: str(uuid.uuid4()))
    # params: BaseModel
    params: Any
