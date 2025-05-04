import asyncio
from datetime import datetime, timedelta, timezone
import logging
from typing import Dict,List
from xecution.common.enums import DataProvider, Exchange, KlineType, Mode, Symbol
from xecution.models.active_order import ActiveOrder
from xecution.models.config import OrderConfig, RuntimeConfig
from xecution.models.topic import DataTopic, KlineTopic
from xecution.services.datasource.cryptoquant import CryptoQuantClient
from xecution.services.exchange.binance_service import BinanceService
from xecution.services.exchange.bybit_service import BybitService
from xecution.services.exchange.okx_service import OkxService

class BaseEngine:
    """Base engine that initializes BinanceService and processes on_candle_closed and on_datasource_update."""

    def __init__(self, config: RuntimeConfig):
        self.config = config
        self.data_map = {}  # Local data storage for kline data
        self.binance_service = BinanceService(config, self.data_map)  # Pass data_map to BinanceService
        self.bybit_service = BybitService(config, self.data_map)  # Pass data_map to BybitService
        self.okx_service = OkxService(config, self.data_map)  # Pass data_map to OkxService
        self.cryptoquant_client = CryptoQuantClient(config, self.data_map)
        self._last_timestamps: Dict[str, int] = {
            topic.url: None for topic in self.config.datasource_topic
        }
        

    async def on_candle_closed(self, kline_topic: KlineTopic):
        """Handles closed candle data"""

    async def on_order_update(self, order):
        """Handles order status"""

    async def on_datasource_update(self, datasource_topic):
        """Handles updates from external data sources."""
        logging.info(f"on_datasource_update: {datasource_topic}")
    
    async def on_active_order_interval(self,activeOrders: list[ActiveOrder]):
        """Handles open orders data."""

    async def start(self):
        """Starts BinanceService and behaves differently based on the runtime mode."""
        try:
            await self.binance_service.get_klines(self.on_candle_closed)
            await self.listen_data_source_update()

            if self.config.mode == Mode.Live or self.config.mode == Mode.Testnet:
                await self.binance_service.check_connection()
                await self.listen_order_status()
                asyncio.create_task(self.listen_open_orders_periodically())
                
                while True:
                    await asyncio.sleep(1)  # Keep the loop alive
            else:
                logging.info("Backtest mode completed. Exiting.")
        except ConnectionError as e:
                logging.error(f"Connection check failed: {e}")
        
    async def place_order(self, order_config: OrderConfig):
        return await self.binance_service.place_order(order_config)
        
    async def get_account_info(self):
        return await self.binance_service.get_account_info()

    async def set_hedge_mode(self, is_hedge_mode: bool):
        return await self.binance_service.set_hedge_mode( is_hedge_mode)

    async def set_leverage(self, symbol: Symbol, leverage: int):
        return await self.binance_service.set_leverage(symbol, leverage)
    
    async def get_position_info(self, symbol: Symbol):
        return await self.binance_service.get_position_info(symbol)
    
    async def get_wallet_balance(self):
        return await self.binance_service.get_wallet_balance()

    async def get_current_price(self,symbol: Symbol):
        if self.config.exchange == Exchange.Binance:
            return await self.binance_service.get_current_price(symbol)
        elif self.config.exchange == Exchange.Bybit:
            return await self.bybit_service.get_current_price(symbol)
        elif self.config.exchange == Exchange.Okx:
            return await self.okx_service.get_current_price(symbol)
        else:
            logging.error("Unknown exchange")
            return None
        
    async def get_order_book(self,symbol:Symbol):
        if self.config.exchange == Exchange.Binance:
            return await self.binance_service.get_order_book(symbol)
        else:
            logging.error("Unknown exchange")
            return None

    async def listen_order_status(self):
        if self.config.exchange == Exchange.Binance:
            return await self.binance_service.listen_order_status(self.on_order_update)
        else:
            logging.error("Unknown exchange")
            return None
        
    async def get_open_orders(self):
        if self.config.exchange == Exchange.Binance:
            # 呼叫 BinanceService 並傳入 on_active_order_interval callback
            return await self.binance_service.get_open_orders(self.on_active_order_interval)
        else:
            logging.error("Unknown exchange")
            
    async def cancel_order(self, symbol:Symbol, client_order_id: str):
        if self.config.exchange == Exchange.Binance:
            return await self.binance_service.cancel_order(symbol, client_order_id)
        else:
            logging.error("Unknown exchange")
    
    async def fetch_data_source(self, data_topic: DataTopic):
        if data_topic.provider == DataProvider.CRYPTOQUANT:
            return await self.cryptoquant_client.fetch_all_parallel(data_topic)

    async def listen_open_orders_periodically(self):
        """
        每 60 秒呼叫一次 Binance 的 get_open_orders API，
        將回傳的 open orders 轉換成 ActiveOrder 後，
        傳給 on_active_order_interval 處理。
        """
        while True:
            try:
                # 由 get_open_orders 內部已使用 on_active_order_interval 處理資料，
                # 這裡只需等待該方法完成即可。
                await self.get_open_orders()
            except Exception as e:
                logging.error("取得 open orders 時發生錯誤: %s", e)
            await asyncio.sleep(60)
            
    async def listen_data_source_update(self):
        """
        Backtest: fetch full history once per topic (via fetch_all_parallel),
        then call on_datasource_update(topic) so you can access the data
        from cryptoquant_client.data_map[topic].

        Live/Testnet: initial fetch to seed last_ts, then every minute:
          - re-fetch full history via fetch_all_parallel
          - diff by timestamp
          - call on_datasource_update(topic, new_items)
        """
        logging.info("Data source listening has started.")
        # --- Backtest: one-shot full history, pass only topic ---
        if self.config.mode == Mode.Backtest:
            for topic in self.config.datasource_topic:
                # fetch entire history into data_map
                await self.cryptoquant_client.fetch_all_parallel(topic)
                # callback with topic only; handler pulls from data_map
                await self.on_datasource_update(topic)
            return

         # --- Live/Testnet: initial seed with most recent bar ---
        for topic in self.config.datasource_topic:
            latest = await self.cryptoquant_client.fetch(topic, last_n=1)
            if latest:
                self._last_timestamps[topic] = latest[-1]["start_time"]

        # align to next full minute
        now      = datetime.now(timezone.utc)
        next_min = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)
        await asyncio.sleep((next_min - now).total_seconds())

        # --- periodic loop every 60s ---
        while True:
            cycle_start = datetime.now(timezone.utc)

            for topic in self.config.datasource_topic:
                try:
                    latest = await self.cryptoquant_client.fetch(topic)
                    if not latest:
                        continue

                    ts      = latest[-1]["start_time"]
                    last_ts = self._last_timestamps.get(topic) or 0

                    if ts > last_ts:
                        # sleep to wait full data enter
                        await asyncio.sleep(30)
                        # callback with only the new record
                        await self.fetch_data_source(topic)
                        await self.on_datasource_update(topic)
                        self._last_timestamps[topic] = ts

                except Exception as e:
                    logging.error("Error fetching %s: %s", topic.url, e)

            # sleep until the top of the next minute
            elapsed = (datetime.now(timezone.utc) - cycle_start).total_seconds()
            await asyncio.sleep(max(0, 60 - elapsed))

