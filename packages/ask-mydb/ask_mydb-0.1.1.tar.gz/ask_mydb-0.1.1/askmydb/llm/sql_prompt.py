def build_sql_prompt(user_question: str, schema: str) -> str:
    """
    Build a consistent prompt for SQL generation from any LLM provider.
    """
    return (
        "You are a SQL expert. Based on the schema and question, write a valid SQL query.\n\n"
        "⚠️ Rules:\n"
        "- Only use tables and columns from the schema.\n"
        "- Do not make up names or values.\n"
        "- Return only valid SQL (no markdown).\n\n"
        f"Schema:\n{schema}\n\n"
        f"Question: {user_question}\n\n"
        "SQL:"
    )

def build_system_prompt() -> str:
    """
    Build a system prompt for SQL generation from any LLM provider.
    """
    system_prompt = (
        "You are an expert SQL generator. Given a database schema and a user question, "
        "generate a syntactically valid and executable SQL query. "
        "Only return the raw SQL (no explanations or markdown formatting). "
        "Avoid using columns or aliases that are not defined. "
        "Ensure all subqueries are logically and syntactically correct, "
        "and avoid ORDER BY or GROUP BY unless explicitly needed. "
        "When using GROUP BY, make sure to group by selected columns correctly. "
        "Respond only with the SQL query string."
    )
    
    return system_prompt
