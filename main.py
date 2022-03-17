from pytest import approx
import requests
import os
import pandas as pd
from terra_sdk.client.lcd import LCDClient

TERRA_ADDRESS = os.environ["TERRA_ADDRESS"]
PLUNA_CONTRACT = "terra1tlgelulz9pdkhls6uglfn5lmxarx7f2gxtdzh2"
YLUNA_CONTRACT = "terra17wkadg0tah554r35x6wvff0y5s7ve8npcjfuhz"
INCREMENT = 0.0001


class Contract:
    def __init__(self, client, contract_address, address):
        self.client = client
        self.contract_address = contract_address
        self.address = address

    def _query_balance(self):
        query = {"balance": {"address": self.address}}
        return self.client.wasm.contract_query(self.contract_address, query)

    def get_balance(self):
        balance_response = self._query_balance()
        info_response = self.client.wasm.contract_info(self.contract_address)

        decimals = info_response["init_msg"]["decimals"]
        return int(balance_response["balance"]) * 10**-decimals


terra_client = LCDClient(chain_id="columbus-5", url="https://lcd.terra.dev")


def get_balances():
    contract_pLuna = Contract(terra_client, PLUNA_CONTRACT, TERRA_ADDRESS)
    contract_yLuna = Contract(terra_client, YLUNA_CONTRACT, TERRA_ADDRESS)

    return contract_pLuna.get_balance(), contract_yLuna.get_balance()


def get_prices():
    url = "https://api.extraterrestrial.money/v1/api/prices"

    response = requests.get(url).json()

    df = pd.json_normalize(pd.DataFrame.from_dict(response)["prices"]).set_index(
        "symbol"
    )

    # luna_price = df.loc["LUNA", "price"]
    # cLuna_price = df.loc["cLUNA", "price"]
    pLuna_price = df.loc["pLUNA", "price"]
    yLuna_price = df.loc["yLUNA", "price"]

    return pLuna_price, yLuna_price


p_pLuna, p_yLuna = get_prices()

pLuna, yLuna = get_balances()

n_pLuna = pLuna
# print(p_pLuna, p_yLuna)

while True:

    if yLuna == approx(pLuna, rel=1e-4):
        break
    else:
        # TODO: Not the best, needs improvement
        if yLuna < pLuna:
            yLuna += (INCREMENT * p_pLuna) / p_yLuna
            pLuna -= INCREMENT
        else:
            pLuna += (INCREMENT * p_yLuna) / p_pLuna
            yLuna -= INCREMENT


print("Luna:", pLuna)
print("pLuna to sell:", n_pLuna - pLuna)
