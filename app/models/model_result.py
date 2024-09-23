from pydantic import BaseModel
from typing import List

class TestCase(BaseModel):
    type: str
    content: List[str]