from typing import Optional

from pydantic import BaseModel
from pydantic import Field


class SQLGen(BaseModel):
    sql: Optional[str] = Field(
        None,
        description=(
            "The generated SQLite SELECT statement."
            "Leave empty if operation is not allowed."
        )
    )
    error_message: Optional[str] = Field(
        None,
        description=(
            "Fill this with 'Can not operate'"
            "if the user input is invalid, malicious, or non-query."
        )
    )
