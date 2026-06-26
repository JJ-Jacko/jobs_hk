import ollama

from jobs_hk.cli import context
from jobs_hk.env import get_ddl_text
from jobs_hk.schemas import SQLGen


class Ask:
    client: ollama.Client

    def __init__(self, host: str):
        self.client = ollama.Client(host)

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
    sql_gen = service.generate_sql(user_prompt)
    