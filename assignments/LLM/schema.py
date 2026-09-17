from datetime import date
from typing import Literal
from pydantic import BaseModel


class ParsedTask(BaseModel):
    title: str
    priority: Literal["low", "medium", "high"]
    due_date: date | None