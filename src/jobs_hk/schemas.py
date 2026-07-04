from typing import Optional
from typing import Literal

from pydantic import BaseModel
from pydantic import Field


class SQLGen(BaseModel):
    status: Literal[
        "REJECT",
        "RESPOND_FAIL",
        "RESPOND_SUCCESS"
    ] = Field(
        ...,
        description="The execution status of the request."
    )
    sql: Optional[str] = Field(
        None,
        description=(
            "The generated SQLite SELECT statement. "
            "MUST be null if status is REJECT or RESPOND_FAIL."
        )
    )
    error_message: Optional[str] = Field(
        None,
        description=(
            "The detailed error reason. "
            "MUST be null if status is REJECT or RESPOND_SUCCESS."
        )
    )
