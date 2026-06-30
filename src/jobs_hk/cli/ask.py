from typing import Dict

import ollama

from jobs_hk.cli import context
from jobs_hk.env import get_ddl_text
from jobs_hk.other import keywords_in_text
from jobs_hk.schemas import SQLGen


class Ask:
    client: ollama.Client
    tools: Dict[str, function]

    def __init__(self, host: str):
        self.client = ollama.Client(host)
        self.tools = {
            "get_jobs_basic_info": context.db.get_jobs_basic_info,
            "generate_sql": self.generate_sql
        }

    def chat(self, user_prompt: str):
        system_prompt = context.project_assistant_p.read_text()
        
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
        
        resp = self.client.chat(
            model=context.project_config["ollama"]["chat_model"],
            messages=messages,
            think=False,
            tools=[
                context.db.get_jobs_basic_info,
                self.generate_sql
            ]
        )
        
        if resp.message.tool_calls:
            messages.append(resp.message)
            for call in resp.message.tool_calls:
                func = self.tools[call.function.name]
                res = func(**call.function.arguments)
                messages.append({
                    "role": "tool",
                    "tool_name": call.function.name,
                    "content": str(res)
                })
            
            resp = self.client.chat(
                model=context.project_config["ollama"]["chat_model"],
                messages=messages,
                think=False,
                options={
                    "num_ctx": 16 * 1024,
                }
            )
        
        return resp.message.content

    def generate_sql(self, user_prompt: str) -> str:
        """Generates a SQLite statement from a direct natural language query.

        Args:
            user_prompt:
                A direct and explicit description of the data query NOT the SQL statement.
                (e.g., "Find jobs with salary upper than 5000"). 
                - CRITICAL: Do NOT use vague or conversational phrasing, or the model will fail.
        """
        
        ddl_text = get_ddl_text()
        system_prompt_template = context.sql_generator_sqlite_only_p.read_text()
        system_prompt = system_prompt_template.format(ddl_text=ddl_text)
        
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
        
        while True:
            resp = self.client.chat(
                model=context.project_config["ollama"]["code_model"],
                messages=messages,
                format=SQLGen.model_json_schema()
            )
            
            sql_gen = SQLGen.model_validate_json(resp.message.content)
            
            # Check attributions `sql` `error_message` exist only one
            has_sql = sql_gen.sql is not None
            has_error_message = sql_gen.error_message is not None
            if not (has_sql ^ has_error_message):
                messages.append(resp.message)
                messages.append({
                    "role": "user",
                    "content": (
                        "Schema violation: You must provide EITHER 'sql' OR 'error_message'."
                        "Do not provide both, and do not leave both empty."
                    )
                })
                continue
            
            # Check attributions `sql` exist
            if not sql_gen.sql:
                messages.append(resp.message)
                messages.append({
                    "role": "user",
                    "content": (
                        f"You provided an error instead of SQL: '{sql_gen.error_message}'."
                        "Please try your best to resolve this and generate a valid SQLite query anyway."
                    )
                })
                continue
            
            # Check sql statement security
            if (
                "SELECT" not in sql_gen.sql
                or keywords_in_text(["INSERT", "UPDATE", "DELETE", "DROP"], sql_gen.sql)
            ):
                messages.append(resp.message)
                messages.append({
                    "role": "user",
                    "content": (
                        "Security/Policy violation: The generated SQL must be a Read-Only 'SELECT' query."
                        "Do NOT use destructive or modification keywords (INSERT, UPDATE, DELETE, DROP)."
                    )
                })
                continue
            
            return sql_gen.sql


def run():
    service = Ask(context.project_config["ollama"]["host"])
    user_prompt = input(">>> ")
    content = service.chat(user_prompt)
    