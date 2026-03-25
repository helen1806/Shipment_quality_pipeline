from dotenv import load_dotenv

import os
from supabase import create_client, Client
import psycopg2
import pandas as pd

load_dotenv()


url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def insert_user_dataset(filename):
    df = pd.read_csv('uploads/'+filename)

    dtype_mapping = {
        "object": "TEXT",
        "int64": "BIGINT",
        "int32": "INTEGER",
        "float64": "DOUBLE PRECISION",
        "float32": "REAL",
        "bool": "BOOLEAN",
        "datetime64[ns]": "TIMESTAMP",
        "timedelta[ns]": "INTERVAL"
    }

    column_defs = []

    for column in df.columns:
        pandas_dtype = df[column].dtype
        postgres_dtype = dtype_mapping.get(pandas_dtype, "TEXT")
        column_defs.append(f'"{column}" {postgres_dtype}')
    
    columns_sql = ", ".join(column_defs)

    table_name = os.path.splitext(filename)[0]

    conn = psycopg2.connect(os.environ.get("DB_URL"))
    cur = conn.cursor()

    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS "{table_name}" (
            {columns_sql}
        )
    """)

    conn.commit()
    cur.close()
    conn.close()

    return (
        supabase.table("user_datasets")
        .insert({
            "table_name": table_name
        })
        .execute()
    )







