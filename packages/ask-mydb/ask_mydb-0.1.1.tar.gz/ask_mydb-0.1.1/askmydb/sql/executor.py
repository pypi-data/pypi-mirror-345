
from sqlalchemy import create_engine, text

def execute_sql(query: str, db_url: str, limit: int = 10, offset: int = 0):
    # Create a connection to the database
    """
    Execute a SQL query on the database and return the results.
    
    Args:
        query (str): _description_
        db_url (str): _description_
        limit (int, optional): _description_. Defaults to 10.
        offset (int, optional): _description_. Defaults to 0.
    """
    
    engine = create_engine(db_url)
    try:
        with engine.connect() as conn:
            # if "limit" not in query.lower():
            #     query += f" LIMIT {limit}"
            # if "offset" not in query.lower():
            #     query += f" OFFSET {offset}"
            
            result = conn.execute(text(query))
            rows = [dict(row._mapping) for row in result]
            return rows
    
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return [{"error": str(e)}]