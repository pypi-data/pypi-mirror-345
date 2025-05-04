import asyncio
import logging
from xecution.models.active_order import ActiveOrder
from xecution.models.config import RuntimeConfig,OrderConfig
from xecution.models.topic import KlineTopic
from xecution.services.connection.base_websockets import WebSocketService
from xecution.services.exchange.binance_helper import BinanceHelper
from xecution.common.enums import Mode, Symbol
from xecution.services.exchange.exchange_order_manager import BinanceOrderManager

class BinanceService:
    
    def __init__(self, config: RuntimeConfig, data_map: dict):
        """
        Binance Service for managing WebSocket and API interactions.
        """
        self.config = config
        self.ws_service = WebSocketService()
        self.data_map = data_map  # External data map reference
        self.binanceHelper = BinanceHelper(self.config)
        self.manager = BinanceOrderManager(
            api_key=config.API_Key,
            api_secret=config.API_Secret,
            mode = config.mode
        )
        
    async def check_connection(self):
        account_info = await self.get_account_info()
        if not account_info or "code" in account_info:  # Binance 錯誤回應通常有 "code"
            error_msg = account_info.get("msg", "Unknown error") if account_info else "No response"
            logging.error(f"[BinanceService] check_connection : API Key validation failed: {error_msg}")
            # Raise an exception to signal failure
            raise ConnectionError(f"API Key validation failed: {error_msg}")
        logging.info(f"[BinanceService] check_connection : Successfully connected to Binance")
    
    async def get_klines(self,on_candle_closed):
        """
        呼叫 Binance /api/v3/klines 取得 K 線
        """
        for kline_topic in self.config.kline_topic :
            if self.config.mode == Mode.Backtest:
                candles = await self.binanceHelper.getKlineRestAPI(kline_topic)
                self.data_map[kline_topic] = candles
                await on_candle_closed(kline_topic)
            elif self.config.mode == Mode.Live or self.config.mode == Mode.Testnet:
                await self.listen_kline(on_candle_closed,kline_topic)

    async def listen_kline(self, on_candle_closed, kline_topic: KlineTopic):
        """Subscribe to Binance WebSocket for a specific kline_topic and handle closed candles."""
        try:
            ws_url = self.binanceHelper.get_websocket_base_url(kline_topic, self.config.mode) + f"/{kline_topic.symbol.value.lower()}@kline_{kline_topic.timeframe.lower()}"
            self.data_map[kline_topic] = []

            async def message_handler(exchange, message):
                """Processes incoming kline messages and calls `on_candle_closed` with `kline_topic`."""
                try:
                    kline = message.get("k", {})
                    if not kline or not kline.get("x", False):
                        return  # Skip invalid or unfinished candles

                    while True:
                        candles = await self.binanceHelper.getLatestKline(kline_topic)
                        converted_kline = self.binanceHelper.convert_ws_kline(kline)
                        ws_start_time = converted_kline.get("start_time")
                        ws_end_time = converted_kline.get("end_time")
                        if any(candle["start_time"] == ws_start_time for candle in candles):
                            self.data_map[kline_topic] = await self.binanceHelper.getKlineRestAPI(kline_topic,ws_end_time)
                            break

                    logging.debug(f"[{exchange}] Candle Closed | {kline_topic.klineType.name}-{kline_topic.symbol}-{kline_topic.timeframe} | Close: {kline.get('c')}")
                    await on_candle_closed(kline_topic)

                except Exception as e:
                    logging.error(f"[BinanceService] on_candle_closed failed: {e}")

            # Subscribe using ws_url and the bound message_handler
            logging.debug(f"[BinanceService] Connecting to WebSocket: {ws_url}")
            await self.ws_service.subscribe(ws_url, ws_url, None, message_handler)
            logging.info(f"[BinanceService] WebSocket subscribed for {kline_topic.klineType.name}-{kline_topic.symbol}-{kline_topic.timeframe}")

        except Exception as e:
            logging.error(f"[BinanceService] listen_kline failed: {e}")
            
    async def listen_order_status(self, on_order_update):
        """
        訂閱 Binance User Data Stream 的 WebSocket，接收訂單更新訊息，
        並在訂單狀態變動時呼叫 on_order_update(order_info)。
        """
        try:
            # 取得 listenKey
            res = await self.manager.get_listen_key()
            listen_key = res.get("listenKey")
            if not listen_key:
                logging.error("[BinanceService] Failed to get listenKey.")
                return

            # 啟動定時保持連線的背景任務
            asyncio.create_task(self._keepalive_listen_key(listen_key))

            # 生成 WebSocket 連線 URL
            ws_url = (
                self.binanceHelper.get_websocket_user_data_base_url(self.config.mode)
                + f"/{listen_key}"
            )
            logging.debug(f"[BinanceService] Connecting to order update stream at {ws_url}")

            # 定義訊息處理函數：如果是訂單更新事件則解析並處理
            async def message_handler(_, message):
                if message.get("e") == "ORDER_TRADE_UPDATE":
                    try:
                        order = self.binanceHelper.parse_order_update(message, self.config.exchange)
                        await on_order_update(order)
                    except Exception as e:
                        logging.error(f"[BinanceService] listen_order_status error: {e}")

            # 訂閱 WebSocket 訊息
            await self.ws_service.subscribe("binance_futures_order", ws_url, None, message_handler)

        except Exception as e:
            logging.error(f"[BinanceService] listen_order_status failed: {e}")


    async def _keepalive_listen_key(self, listen_key):
        """
        定時呼叫 keepalive 以保持 listenKey 的有效性，每 30 分鐘呼叫一次。
        """
        while True:
            try:
                await self.manager.keepalive_listen_key(listen_key)
            except Exception as e:
                logging.error(f"[BinanceService] keepalive error: {e}")
            await asyncio.sleep(30 * 60)

    async def place_order(self, order_config: OrderConfig):
        # 檢查是否已有未成交訂單，避免重複下單
        return self.binanceHelper.parse_order_response(await self.manager.place_order(order_config))
        
    async def get_account_info(self):
        account_info = await self.manager.get_account_info()
        return account_info
    
    async def get_wallet_balance(self):
        wallet_balance = await self.manager.get_wallet_balance()
        return wallet_balance
    
    async def set_hedge_mode(self,is_hedge_mode: bool):
        await self.manager.set_hedge_mode(is_hedge_mode) 
        
    async def set_leverage(self,symbol: Symbol, leverage: int):
        await self.manager.set_leverage(symbol,leverage)
    
    async def get_position_info(self, symbol: Symbol):
        return await self.manager.get_position_info(symbol)

    async def get_current_price(self,symbol: Symbol):
        return await self.manager.get_current_price(symbol)
    
    async def get_order_book(self,symbol:Symbol):
        orderbook  = self.binanceHelper.parse_order_book(await self.manager.get_order_book(symbol)) 
        logging.info(f"[BinanceService] get_order_book: {orderbook}")
        return orderbook
    
    async def get_open_orders(self,on_active_order_interval) :
        orders = await self.manager.get_open_orders()
        active_orders = [self.binanceHelper.convert_order_to_active_order(order) for order in orders]
        return await on_active_order_interval(active_orders) 

    async def cancel_order(self, symbol, client_order_id):
        return await self.manager.cancel_order(symbol, client_order_id)