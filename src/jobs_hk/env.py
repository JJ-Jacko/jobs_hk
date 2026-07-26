import sqlalchemy.dialects as dialects
from sqlalchemy.schema import CreateTable
from sqlmodel import SQLModel

def get_ddl_text():
    ddl_text = ""
    
    for table in SQLModel.metadata.sorted_tables:
        sql_compiled = CreateTable(table).compile(dialect=dialects.sqlite.dialect())
        ddl_text += f"{str(sql_compiled).strip()};\n\n"
    
    return ddl_text