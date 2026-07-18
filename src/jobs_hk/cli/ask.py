import jobs_hk.context as context
from jobs_hk.services.assistant import Assistant

    
def run():
    service = Assistant(context.project_config["ollama"]["host"])
    
    while True:
        user_prompt = input(">>> ")
        content = service.chat(user_prompt)
        print(content)
        print('=' * 60)