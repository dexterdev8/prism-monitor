from pytest import approx
import requests
import os
import pandas as pd
from terra_sdk.client.lcd import LCDClient
from terra_sdk.client.lcd.api import bank

TERRA_ADDRESS = os.environ["TERRA_ADDRESS"]
PLUNA_CONTRACT = "terra1tlgelulz9pdkhls6uglfn5lmxarx7f2gxtdzh2"
INCREMENT = 0.0001

yLuna = 0
pLuna = 58241.935
n_pLuna = pLuna


def get_balance():
    terra_client = LCDClient(chain_id="columbus-5", url="https://lcd.terra.dev")
    print(
        terra_client.wasm.contract_query(
            PLUNA_CONTRACT, {"balance": {"address": TERRA_ADDRESS}}
        )
    )
    bank_instance = bank.BankAPI(terra_client)
    balance = bank_instance.balance(TERRA_ADDRESS)
    print(balance[0])


def get_prices():
    url = "https://api.extraterrestrial.money/v1/api/prices"

    response = requests.get(url).json()

    df = pd.json_normalize(pd.DataFrame.from_dict(response)["prices"]).set_index(
        "symbol"
    )

    luna_price = df.loc["LUNA", "price"]
    pLuna_price = df.loc["pLUNA", "price"]
    yLuna_price = df.loc["yLUNA", "price"]

    return pLuna_price, yLuna_price


p_pLuna, p_yLuna = get_prices()

get_balance()

while True:

    if yLuna == approx(pLuna, rel=1e-5):
        break
    else:
        yLuna += (INCREMENT * p_pLuna) / p_yLuna
        pLuna -= INCREMENT


print("Luna:", pLuna)
print("pLuna to sell:", n_pLuna - pLuna)
