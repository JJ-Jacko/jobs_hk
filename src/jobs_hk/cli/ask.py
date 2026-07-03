from typing import Dict

import ollama

from jobs_hk.cli import context
from jobs_hk.env import get_ddl_text
from jobs_hk.exceptions import ModelGenerateException
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
            messages.append(resp.message)
            
            # Check status in rule
            if sql_gen.status not in ["REJECT", "RESPOND_FAIL", "RESPOND_SUCCESS"]:
                messages.append({
                    "role": "user",
                    "content": "Schema violation: `status` MUST fill with REJECT, RESPOND_FAIL and RESPOND_SUCCESS"
                })
                continue
            
            if sql_gen.status == "REJECT":
                if sql_gen.sql is not None and sql_gen.error_message is not None:
                    messages.append({
                        "role": "user",
                        "content": (
                            "Schema violation: If `status` is REJECT, "
                            "fill `sql`, `error_message` both with null."
                        )
                    })
                    continue
                
                raise ModelGenerateException(
                    type="REJECT",
                    model_content=resp.message.content,
                    message=(
                        "The request is invalid, malicious, non-query or irrelevant conversational text "
                        "or tries to INSERT/UPDATE/DELETE/DROP these illegal modification."
                    )
                )
            
            if sql_gen.status == "RESPOND_FAIL":
                if sql_gen.sql is not None or sql_gen.error_message is None:
                    messages.append({
                        "role": "user",
                        "content": (
                            "Schema violation: If `status` is RESPOND_FAIL, "
                            "fill `sql` with null, "
                            "fill `error_message` with the spcific reason."
                        )
                    })
                    continue
                
                raise ModelGenerateException(
                    type="RESPOND_FAIL",
                    model_content=resp.message.content,
                    message="The request is a query intent but cannot be fulfilled due to missing data/tables."
                )
            
            # Check sql statement security
            if (
                "SELECT" not in sql_gen.sql
                or keywords_in_text(["INSERT", "UPDATE", "DELETE", "DROP"], sql_gen.sql)
            ):
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
    