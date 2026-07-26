import jobs_hk.context as context
from jobs_hk.db import DB
from jobs_hk.services.assistant import Assistant

    
def run():
    db = DB(context.DATA_BASE_FILE)
    service = Assistant(
        host=context.CONFIG["ollama"]["host"],
        db=db
    )
    
    while True:
        user_prompt = input(">>> ")
        content = service.chat(user_prompt)
        print(content)
        print('=' * 60)