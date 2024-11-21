from dotenv import load_dotenv
import os

def test_env():
    load_dotenv()
    api_key = os.getenv('RH_API_KEY')
    private_key = os.getenv('RH_PRIVATE_KEY')
    
    print("API Key found:", "Yes" if api_key else "No")
    print("Private Key found:", "Yes" if private_key else "No")
    
    if api_key and private_key:
        print("\nAPI Key format correct:", api_key.startswith("rh-api-"))
        print("Private Key format correct:", len(private_key) > 20 and "=" in private_key)

if __name__ == "__main__":
    test_env()