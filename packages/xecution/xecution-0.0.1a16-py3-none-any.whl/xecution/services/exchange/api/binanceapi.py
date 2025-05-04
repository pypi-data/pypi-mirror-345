# excution/service/exchange/api/binanceapi.py

import hashlib
import hmac
import logging
import time
from urllib.parse import urlencode
from ...connection.restapi import RestAPIClient  # 注意引用路徑

logger = logging.getLogger(__name__)

class BinanceAPIClient(RestAPIClient):
    """
    專門給 Binance 用的 API 客戶端。
    - 若需要簽名時，就 override _sign_request()
    - 若要 Binance 特定錯誤處理，就 override _handle_response()
    """

    def __init__(self, api_key: str = None, api_secret: str = None):
        super().__init__()
        self.api_key = api_key
        self.api_secret = api_secret

    async def request(self, method: str, url: str, params: dict = {}, auth: bool = False):
        """
        改寫 request() 以整合 Binance 特定 header & 簽名
        """
        await self.init_session()
        try:
            if(auth):
                # 1. 準備參數副本
                params = params.copy()
                params["timestamp"] = int(time.time() * 1000)
                params["recvWindow"] = 5000
                # 2. 產生 query string（要排序）
                query_string = urlencode(sorted(params.items()))
                # 3. 簽名
                signature = hmac.new(self.api_secret.encode(), query_string.encode(), hashlib.sha256).hexdigest()
                url = f"{url}?{query_string}&signature={signature}"
                # 4. 設定 header
                headers = {
                    "X-MBX-APIKEY": self.api_key,
                    "Content-Type": "application/json"
                }
                return await super().signed_request(method, url,headers)
            else:
                return await super().request(method, url, params=params)
        # 呼叫父類別 (RestAPIClient) 的 request
        except Exception as e:
            raise Exception(f"\n[BinanceAPIClient] request failed: {e}")
            
    async def close(self):
        await super().close()