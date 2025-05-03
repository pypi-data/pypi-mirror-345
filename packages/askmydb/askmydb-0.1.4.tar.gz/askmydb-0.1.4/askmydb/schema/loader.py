


from sqlalchemy import create_engine, inspect


def load_schema(db_url:str) -> str:
    """
    Load the database schema from the given URL.
    
    Args:
        db_url (str): The database URL.
    
    Returns:
        str: The database schema.
    """
    
    engine = create_engine(db_url)
    inspector = inspect(engine)
    
    schema_info = []
    
    for table in inspector.get_table_names():
        schema_info.append(f"Table: {table}")
        columns = inspector.get_columns(table)
        for column in columns:
            schema_info.append(f"  Column: {column['name']} - Type: {column['type']}")
        schema_info.append("")
        
    return "\n".join(schema_info)