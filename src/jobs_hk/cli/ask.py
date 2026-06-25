from typing import Optional

import ollama
from pydantic import BaseModel
from pydantic import Field

import jobs_hk.cli.context as context
from jobs_hk.env import get_ddl_text


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


def run():
    client = ollama.Client(context.project_config["ollama"]["host"])
    ddl_text = get_ddl_text()
    system_prompt_template = context.sql_generator_sqlite_only_p.read_text()
    system_prompt = system_prompt_template.format(ddl_text=ddl_text)
    
    user_prompt = input(">>> ")
    
    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": user_prompt
        }
    ]
    
    resp = client.chat(
        model=context.project_config["ollama"]["model"],
        messages=messages,
        format=SQLGen.model_json_schema()
    )
    sql_gen = SQLGen.model_validate_json(resp.message.content)
    