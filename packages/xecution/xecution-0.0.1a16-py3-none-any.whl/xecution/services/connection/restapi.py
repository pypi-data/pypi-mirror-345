from urllib.parse import urlencode
import aiohttp
import logging

logger = logging.getLogger(__name__)

class RestAPIClient:
    """
    通用的 REST API 客戶端骨架。
    如果你想在這裡做共用的錯誤處理，可以寫在 _handle_response。
    但 Binance/Bybit/OKX 各有不同錯誤碼邏輯時，
    可以選擇在子類別（binanceapi.py 等）裡覆寫 _handle_response()。
    """
    def __init__(self):
        self.session = None

    async def init_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()

    async def _handle_response(self, response):
        try:
            if response.status != 200:
                text = await response.text()
                raise Exception(f"\n[HTTP {response.status}] Error: {text}")
            
            return await response.json()
        except Exception as err:
            raise err

    async def request(self, method: str, url: str, params: dict = None, headers: dict = None, timeout: int = 10):
        await self.init_session()
        params = params or {}
        headers = headers or {"Content-Type": "application/json"}
        try:
            async with self.session.request(
                method=method.upper(),
                url=url,
                params=params if method.upper() == "GET" else None,
                json=params if method.upper() == "POST" else None,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as resp:
                return await self._handle_response(resp)
        except Exception as e:
            raise Exception(f"\n[{method}] request to {url} failed: {e}")

    async def signed_request(self, method: str, url: str, headers: dict, timeout: int = 10):
        await self.init_session()
        # 5. 發送請求（注意：不能再帶 json=params，會造成 body 混淆）
        try:
            async with self.session.request(
                method=method.upper(),
                url=url,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as resp:
                return await self._handle_response(resp)
        except Exception as e:
            raise Exception(f"\n[{method}] request to {url} failed: {e}")

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()