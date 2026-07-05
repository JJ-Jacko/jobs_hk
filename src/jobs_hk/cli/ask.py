from jobs_hk.cli import context
from jobs_hk.services.assistant import Assistant

    
def run():
    service = Assistant(context.project_config["ollama"]["host"])
    
    while True:
        user_prompt = "I want to find a job about sale"
        content = service.chat(user_prompt)
        print(content)
        print('=' * 60)