from azure.identity import DefaultAzureCredential
import datetime

def test_token():
    print("---  Vault Authentication Test ---")
    try:
        credential = DefaultAzureCredential()
        print("Requesting token for Azure SQL...")
        token = credential.get_token("https://database.windows.net/.default")
        expiry = datetime.datetime.fromtimestamp(token.expires_on)
        print(" SUCCESS!")
        print(f"Token acquired. It expires at: {expiry}")
    except Exception as e:
        print(f" AUTHENTICATION FAILED: {e}")

if __name__ == "__main__":
    test_token()