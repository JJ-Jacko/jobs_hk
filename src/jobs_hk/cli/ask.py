import jobs_hk.context as context
from jobs_hk.db import DB
from jobs_hk.services.assistant import Assistant

    
def main():
    db = DB(context.DATA_BASE_FILE, read_only=True)
    service = Assistant(db)
    
    while True:
        user_prompt = input(">>> ")
        content = service.chat(user_prompt)
        print(content)
        print('=' * 60)


if __name__ == "__main__":
    main()
    