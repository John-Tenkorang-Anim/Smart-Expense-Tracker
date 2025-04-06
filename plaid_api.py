from plaid import Client
from config import PLAID_CLIENT_ID, PLAID_SECRET, PLAID_ENV

plaid_client = Client(client_id=PLAID_CLIENT_ID, secret=PLAID_SECRET, environment=PLAID_ENV)

def get_transactions(access_token):
    response = plaid_client.Transactions.get(access_token, start_date="2024-01-01", end_date="2024-04-01")
    return response['transactions']
