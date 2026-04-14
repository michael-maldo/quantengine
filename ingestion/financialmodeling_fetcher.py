import os
from dotenv import load_dotenv
import requests
from enum import Enum

load_dotenv()
key = os.getenv("FINANCIAL_MODELING_API_KEY")

def fetch_symbols(type):
    url=f"https://financialmodelingprep.com/stable/{type}?apikey={key}"

    response = requests.get(url, timeout=10)
    return response.json()