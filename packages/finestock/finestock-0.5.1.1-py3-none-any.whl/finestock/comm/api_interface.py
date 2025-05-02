from abc import ABC, abstractmethod


class IAPI(ABC):
    @abstractmethod
    def oauth(self):
        raise NotImplemented

    @abstractmethod
    def set_oauth_info(self, app_key, app_secret):
        raise NotImplemented

    @abstractmethod
    def set_access_token(self, token):
        raise NotImplemented

    @abstractmethod
    def get_ohlcv(self, code, frdate, todate):
        raise NotImplemented

    @abstractmethod
    def get_index(self, code, frdate, todate):
        raise NotImplemented

    @abstractmethod
    def get_orderbook(self, code):
        raise NotImplemented

    @abstractmethod
    def set_queue(self, queue, condition):
        raise NotImplemented

    @abstractmethod
    def set_price_queue(self, price_queue, condition):
        raise NotImplemented

    @abstractmethod
    def set_trade_queue(self, trade_queue, condition):
        raise NotImplemented

    @abstractmethod
    def set_orderbook_queue(self, orderbook_queue, condition):
        raise NotImplemented

    @abstractmethod
    async def recv_price(self, code, status=True):
        raise NotImplemented

    @abstractmethod
    async def recv_index(self, code, status=True):
        raise NotImplemented

    @abstractmethod
    async def recv_orderbook(self, code, status=True):
        raise NotImplemented

    @abstractmethod
    async def recv_trade(self, code, status=True):
        raise NotImplemented
