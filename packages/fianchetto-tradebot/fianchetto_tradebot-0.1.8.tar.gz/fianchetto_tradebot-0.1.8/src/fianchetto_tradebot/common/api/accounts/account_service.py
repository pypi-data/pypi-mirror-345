from fianchetto_tradebot.common.api.accounts.account_list_response import AccountListResponse
from fianchetto_tradebot.common.api.accounts.get_account_balance_request import GetAccountBalanceRequest
from fianchetto_tradebot.common.api.accounts.get_account_balance_response import GetAccountBalanceResponse
from fianchetto_tradebot.common.api.accounts.get_account_info_request import GetAccountInfoRequest
from fianchetto_tradebot.common.api.accounts.get_account_info_response import GetAccountInfoResponse
from fianchetto_tradebot.common.api.api_service import ApiService
from fianchetto_tradebot.common.exchange.connector import Connector


class AccountService(ApiService):
    def __init__(self, connector: Connector):
        super().__init__(connector)
        
    def list_accounts(self) -> AccountListResponse:
        pass

    def get_account_info(self, get_account_info_request: GetAccountInfoRequest) -> GetAccountInfoResponse:
        pass

    def get_account_balance(self, get_account_balance_request: GetAccountBalanceRequest)-> GetAccountBalanceResponse:
        pass

