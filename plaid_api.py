# plaid_api.py

import os
from datetime import date
from plaid.api import plaid_api
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.configuration import Configuration
from plaid.api_client import ApiClient
from plaid import Environment
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID")
PLAID_SECRET = os.getenv("PLAID_SECRET")
PLAID_ENV = os.getenv("PLAID_ENV", "sandbox")  # 'sandbox', 'development', or 'production'

host = Environment.SANDBOX
if PLAID_ENV == "development":
    host = Environment.DEVELOPMENT
elif PLAID_ENV == "production":
    host = Environment.PRODUCTION

configuration = Configuration(
    host=host,
    api_key={
        'clientId': PLAID_CLIENT_ID,
        'secret': PLAID_SECRET,
    }
)

api_client = ApiClient(configuration)
plaid_client = plaid_api.PlaidApi(api_client)

# 🔗 Create a link token for frontend
def create_link_token(user_id):
    request = LinkTokenCreateRequest(
        user=LinkTokenCreateRequestUser(client_user_id=user_id),
        client_name="Smart Expense Tracker",
        products=[Products("transactions")],
        country_codes=[CountryCode("US")],
        language="en"
    )
    response = plaid_client.link_token_create(request)
    return response.to_dict()

# 🔐 Exchange public token for access token
def exchange_public_token(public_token):
    request = ItemPublicTokenExchangeRequest(public_token=public_token)
    response = plaid_client.item_public_token_exchange(request)
    return response.to_dict()

# 💳 Get transactions
def get_transactions(access_token):
    request = TransactionsGetRequest(
        access_token=access_token,
        start_date=date(2024, 1, 1),
        end_date=date.today()
    )
    response = plaid_client.transactions_get(request)
    return response.to_dict()["transactions"]

# 💰 Get account balances
def get_balances(access_token):
    request = AccountsBalanceGetRequest(access_token=access_token)
    response = plaid_client.accounts_balance_get(request)
    return response.to_dict()["accounts"]