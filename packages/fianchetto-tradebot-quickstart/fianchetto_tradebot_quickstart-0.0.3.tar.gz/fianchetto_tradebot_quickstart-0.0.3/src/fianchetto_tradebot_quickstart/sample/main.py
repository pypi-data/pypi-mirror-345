import configparser
import os
from enum import Enum

import requests
from fianchetto_tradebot.common.exchange.exchange_name import ExchangeName
from fianchetto_tradebot.oex.serving.oex_rest_service import OexRestService
from fianchetto_tradebot.quotes.serving.quotes_rest_service import QuotesRestService

from runnable_service import RunnableService
from concurrent.futures import ThreadPoolExecutor

config = configparser.ConfigParser()
ACCOUNT_ID_KEY = 'ACCOUNT_ID_KEY'
ACCOUNT_KEY = 'ACCOUNT_ID'
ETRADE_CONFIGURATION_FILE = os.path.join(os.path.dirname(__file__), './config/etrade_config.ini')
SCHWAB_CONFIGURATION_FILE = os.path.join(os.path.dirname(__file__), './config/schwab_config.ini')
IKBR_CONFIGURATION_FILE = os.path.join(os.path.dirname(__file__), './config/ikbr_config.ini')

ACCOUNTS_CONFIGURATION_FILE = os.path.join(os.path.dirname(__file__), './config/accounts.ini')
SERVICE_CONFIGURATION_FILE = os.path.join(os.path.dirname(__file__), './config/service_config.ini')


services: list[RunnableService] = []
executor = ThreadPoolExecutor(max_workers=10)

class ServiceKey(Enum):
    OEX = "oex"
    QUOTES = "quotes"
    TRIDENT = "trident"
    HELM = "helm"

def start_all_services():
    # Get all configurations
    credential_dict: dict[ExchangeName, str] = {
        ExchangeName.ETRADE : ETRADE_CONFIGURATION_FILE,
        ExchangeName.SCHWAB : SCHWAB_CONFIGURATION_FILE,
        ExchangeName.IKBR : IKBR_CONFIGURATION_FILE
    }

    config.read(SERVICE_CONFIGURATION_FILE)
    ports_dict: dict[ServiceKey, int] = {
        ServiceKey.OEX : config.getint('PORTS', 'OEX_SERVICE_PORT'),
        ServiceKey.QUOTES : config.getint('PORTS', 'QUOTES_SERVICE_PORT'),
        ServiceKey.TRIDENT :config.getint('PORTS', 'TRIDENT_SERVICE_PORT'),
        ServiceKey.HELM : config.getint('PORTS', 'HELM_SERVICE_PORT'),
    }

    invoke_oex_service(credential_dict, ports_dict[ServiceKey.OEX])
    invoke_quotes_service(credential_dict, ports_dict[ServiceKey.QUOTES])
    # TODO: Add the rest of the services

    print("Up & Running!")

def invoke_quotes_service(credential_dict: dict[ExchangeName, str], port=8081):
    quotes_service = QuotesRestService(credential_config_files=credential_dict)
    quotes_runnable = RunnableService(port, quotes_service)

    services.append(quotes_runnable)
    executor.submit(quotes_runnable)

def invoke_oex_service(credential_dict: dict[ExchangeName, str], port=8080):
    oex_service = OexRestService(credential_config_files=credential_dict)
    oex_runnable = RunnableService(port, oex_service)

    services.append(oex_runnable)
    executor.submit(oex_runnable)

def get_orders():
    config.read(ACCOUNTS_CONFIGURATION_FILE)
    accounts_dict: dict[ExchangeName, str] = {
        ExchangeName.ETRADE : config.get('ETRADE', ACCOUNT_ID_KEY, fallback=None),
        ExchangeName.IKBR : config.get('IKBR', ACCOUNT_KEY, fallback=None),
        ExchangeName.SCHWAB : config.get('SCHWAB', ACCOUNT_KEY, fallback=None)
    }

    e_trade_account_id = accounts_dict[ExchangeName.ETRADE]

    print(f'Hi, we\'re going list orders for {ExchangeName.ETRADE}')  # Press ⌘F8 to toggle the breakpoint.
    host='0.0.0.0'
    port=8080
    response = requests.get(f"http://{host}:{port}/api/v1/{ExchangeName.ETRADE.value}/{e_trade_account_id}/orders")

    print(response)


if __name__ == '__main__':
    start_all_services()
    get_orders()
