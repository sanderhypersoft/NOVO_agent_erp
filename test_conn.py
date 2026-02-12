import os
import httpx
from dotenv import load_dotenv

load_dotenv()

def test():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    print(f"Testing connection to: {url}")
    try:
        # Tenta um GET simples na raiz do API
        response = httpx.get(f"{url}/rest/v1/", headers={"apikey": key, "Authorization": f"Bearer {key}"})
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:100]}")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    test()
