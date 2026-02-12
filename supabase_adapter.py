import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class SupabaseAdapter:
    def __init__(self):
        url: str = os.environ.get("SUPABASE_URL")
        key: str = os.environ.get("SUPABASE_KEY")
        if not url or not key:
            raise ValueError("SUPABASE_URL or SUPABASE_KEY not found in environment")
        self.supabase: Client = create_client(url, key)

    def get_semantic_dictionary(self):
        return self.supabase.table("semantic_dictionary").select("*").execute()

    def get_operational_dictionary(self):
        return self.supabase.table("operational_dictionary").select("*").execute()

    def log_intelligence(self, data):
        return self.supabase.table("intelligence_log").insert(data).execute()

    def upsert_semantic(self, data):
        return self.supabase.table("semantic_dictionary").upsert(data).execute()

    def upsert_operational(self, data):
        return self.supabase.table("operational_dictionary").upsert(data).execute()
