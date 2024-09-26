from pydantic import BaseModel
from typing import List

import uuid
import time
import os

class TestCase(BaseModel):
    type: str
    content: List[str]


    