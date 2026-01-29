import pandas as pd
from sqlalchemy import create_engine, text
import os

# Database connection details from env
DB_USER = os.getenv("DB_USER", "odoo")
DB_PASSWORD = os.getenv("DB_PASSWORD", "odoo")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5433")
DB_NAME = os.getenv("DB_NAME", "postgres")

# Create SQLAlchemy engine
# url format: postgresql://user:password@host:port/dbname
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)

def get_dataframe(query: str) -> pd.DataFrame:
    """
    Executes a raw SQL query and returns the result as a Pandas DataFrame.
    
    Args:
        query (str): The SQL query to execute.
        
    Returns:
        pd.DataFrame: The result of the query.
    """
    try:
        with engine.connect() as connection:
            df = pd.read_sql(text(query), connection)
        return df
    except Exception as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame() # Return empty DataFrame on error
