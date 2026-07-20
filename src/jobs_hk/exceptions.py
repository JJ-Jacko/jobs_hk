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


class SQLStatementExecException(Exception):
    statement: str
    reason: str
    
    def __init__(
            self,
            statement: str,
            reason: str
    ):
        self.statement = statement
        self.reason = reason

    def __str__(self):
        return (
            f"statement: `{self.statement}` is illegal.\n"
            f"reason: {self.reason}."
        )


class ProxyServerDisconnection(Exception):
    host: str
    port: int
    
    def __init__(
            self,
            host: str,
            port: str
    ):
        self.host = host
        self.port = port

    def __str__(self):
        return f"Server: `{self.host}:{self.port}` is disconnection."


class WebRetryExansted(Exception):
    ...
