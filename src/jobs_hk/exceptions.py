from typing import Literal


class ModelGenerateException(Exception):
    type: str
    model_content: str
    message: str
    
    def __init__(
            self,
            type: str,
            model_content: str,
            message: str
    ):
        self.type = type
        self.model_content = model_content
        self.message = message
    
    def __str__(self):
        return self.message
