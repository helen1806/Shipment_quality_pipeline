from dotenv import load_dotenv

import os
from supabase import create_client, Client
import psycopg2
import pandas as pd

load_dotenv()
db_url = os.environ.get("DB_URL")

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def insert_user_dataset(table_name):
    
    table_name = os.path.splitext(table_name)[0]
    
    return (
        supabase.table("user_datasets")
        .insert({
            "table_name": table_name
        })
        .execute()
    )

    
conn = psycopg2.connect(db_url)
cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS {table_name} (
        id SERIAL PRIMARY KEY,
        name TEXT,
        city TEXT
    )
""")

conn.commit()
cur.close()
conn.close()




