from dotenv import load_dotenv
import os
import psycopg2
import pandas as pd

load_dotenv()

_supabase_client = None

def get_supabase():
    global _supabase_client
    if _supabase_client is None:
        from supabase import create_client
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        if not url or not key:
            raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set in your .env file")
        _supabase_client = create_client(url, key)
    return _supabase_client


def insert_user_dataset(filename, df):
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
    schema_info = []

    for column in df.columns:
        pandas_dtype = str(df[column].dtype)
        postgres_dtype = dtype_mapping.get(pandas_dtype, "TEXT")
        column_defs.append(f'"{column}" {postgres_dtype}')
        schema_info.append({"column": column, "type": postgres_dtype})

    columns_sql = ", ".join(column_defs)
    table_name = os.path.splitext(filename)[0]

    uploads_path = os.path.join(os.path.dirname(__file__), "uploads", filename)
    df.to_csv(uploads_path, index=False)

    db_url = os.environ.get("DB_URL") or os.environ.get("DATABASE_URL")
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    cur.execute(f'DROP TABLE IF EXISTS "{table_name}"')
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS "{table_name}" (
            {columns_sql}
        )
    """)

    with open(uploads_path, "r", encoding="utf-8") as f:
        cur.copy_expert(
            f'COPY "{table_name}" FROM STDIN WITH CSV HEADER',
            f
        )

    conn.commit()
    cur.close()
    conn.close()

    try:
        get_supabase().table("user_datasets").upsert({
            "table_name": table_name
        }).execute()
    except Exception:
        pass

    return {
        "table_name": table_name,
        "rows": len(df),
        "columns": len(df.columns),
        "schema": schema_info
    }


def get_uploaded_tables():
    try:
        result = get_supabase().table("user_datasets").select("table_name").execute()
        return [row["table_name"] for row in result.data]
    except Exception:
        return []
