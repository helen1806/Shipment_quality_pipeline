from dotenv import load_dotenv

import os
from supabase import create_client, Client

load_dotenv()
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