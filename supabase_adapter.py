import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class SupabaseAdapter:
    def __init__(self):
        self.url: str = os.environ.get("SUPABASE_URL")
        self.key: str = os.environ.get("SUPABASE_KEY")
        self.supabase = None
        
        if self.url and self.key:
            try:
                self.supabase: Client = create_client(self.url, self.key)
            except Exception as e:
                print(f"DEBUG: Falha ao inicializar cliente Supabase: {e}")
        else:
            print("DEBUG: SUPABASE_URL ou SUPABASE_KEY não configurados.")

    def get_semantic_dictionary(self):
        if not self.supabase: return None
        return self.supabase.table("semantic_dictionary").select("*").execute()

    def get_operational_dictionary(self):
        if not self.supabase: return None
        return self.supabase.table("operational_dictionary").select("*").execute()

    def log_intelligence(self, data):
        if not self.supabase: return None
        return self.supabase.table("intelligence_log").insert(data).execute()

    def upsert_semantic(self, data):
        return self.supabase.table("semantic_dictionary").upsert(data).execute()

    def upsert_operational(self, data):
        return self.supabase.table("operational_dictionary").upsert(data).execute()
