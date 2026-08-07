from typing import Dict

import openai

import jobs_hk.context as context
from jobs_hk.exceptions import ModelGenerateException
from jobs_hk.exceptions import SQLStatementExecException
from jobs_hk.db import DB
from jobs_hk.other import keywords_in_text
from jobs_hk.schemas import SQLGen


__all__ = ["Assistant"]


class Assistant:
    client: openai.Client
    db: DB
    tools: Dict[str, function]

    def __init__(self, db: DB):
        self.client = openai.Client(
            api_key=context.MOONSHOT_API_KEY,
            base_url=context.BASE_URLS.MOONSHOT
        )
        self.db = db
        self.tools = {
            "get_jobs_basic_info": self.db.get_jobs_basic_info,
            "query_jobs_database": self.query_jobs_database
        }

    def chat(self, user_prompt: str):
        system_prompt = context.PROMPTS.PROJECT_ASSISTANT.read_text()
        
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
            model=context.CONFIG["ollama"]["chat_model"],
            messages=messages,
            think=False,
            tools=self.tools.values()
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
                model=context.CONFIG["ollama"]["chat_model"],
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
        
        ddl_text = self.db.get_ddl_text()
        system_prompt_template = context.PROMPTS.SQL_GENERATOR.read_text()
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
            completion = self.client.chat.completions.parse(
                model=context.CONFIG["LLM"]["code_model"],
                messages=messages,
                response_format=SQLGen
            )
            content = completion.choices[0].message.content
            sql_gen = completion.choices[0].message.parsed
            messages.append(completion.choices[0].message)
            
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
                    model_content=content,
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
                    model_content=content,
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
                        "Security/Policy violation: The generated SQL must be a Read-Only 'SELECT' query. "
                        "Do NOT use destructive or modification keywords (INSERT, UPDATE, DELETE, DROP)."
                    )
                })
                continue
            
            return sql_gen.sql

    def query_jobs_database(self, user_prompt: str):
        """
        Query the database using a natural language descripion.
        
        Convert the request into a SQL SELECT statement and executes it,
        returning matching records or an error description
        if the query cound not be fulfilled.

        Args:
            user_prompt:
                A direct and explicit description of the data query NOT the SQL statement.
                (e.g., "Find jobs with salary upper than 5000"). 
                - CRITICAL: Do NOT use vague or conversational phrasing, or the model will fail.
        """
        
        try:
            statement = self.generate_sql(user_prompt)
        except ModelGenerateException as e:
            return (
                "Query execution FAILED.\n"
                f"Reason: {str(e)}\n"
                "Attention: Do NOT expose raw SQL or technical error datails to the user, "
                "instead, explain in natural language that the request could not be fulfilled "
                "and suggest the user or simplify their query."
            )
        
        try:
            info = self.db.get_jobs_specific_info(statement)
        except SQLStatementExecException as e:
            return (
                "Query execution FAILED.\n"
                f"Reason: {str(e)}\n"
                "Attention: Do NOT expose raw SQL or technical error datails to the user, "
                "instead, explain in natural language that the request could not be fulfilled "
                "and suggest the user or simplify their query."
            )
        else:
            return (
                "Query execution SUCCESSED.\n"
                f"Result: {str(info)}"
            )
        
