from typing import Dict

import ollama

from jobs_hk.cli import context
from jobs_hk.env import get_ddl_text
from jobs_hk.schemas import SQLGen


class Ask:
    client: ollama.Client
    tools: Dict[str, function]

    def __init__(self, host: str):
        self.client = ollama.Client(host)
        self.tools = {
            "get_jobs_basic_info": context.db.get_jobs_basic_info,
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
            tools=[context.db.get_jobs_basic_info]
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

    def generate_sql(self, user_prompt: str):
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
        
        resp = self.client.chat(
            model=context.project_config["ollama"]["code_model"],
            messages=messages,
            format=SQLGen.model_json_schema()
        )
        
        return SQLGen.model_validate_json(resp.message.content)
    

def run():
    service = Ask(context.project_config["ollama"]["host"])
    user_prompt = input(">>> ")
    content = service.chat(user_prompt)
    