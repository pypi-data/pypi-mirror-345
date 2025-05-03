from pydantic import BaseModel
from pydantic.fields import Field
import uuid
from typing import Any

class MethodCall(BaseModel):
    service: str
    method: str
    fancy_key: str = Field(default_factory=lambda: str(uuid.uuid4()))
    params: Any

call1 = MethodCall(service="user_service", method="create_user", params={"name": "Alice"})
call2 = MethodCall(service="product_service", method="get_product", params={"id": 123})

print(f"Call 1 fancy_key: {call1.fancy_key}")
print(f"Call 2 fancy_key: {call2.fancy_key}")