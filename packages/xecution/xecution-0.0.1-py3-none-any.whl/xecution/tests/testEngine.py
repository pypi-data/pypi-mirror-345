import asyncio
import sys

if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
else:
    sys.path.append("/Users/kaihock/Desktop/All In/Xecution")

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timezone
from xecution.core.engine import BaseEngine
from xecution.common.enums import DataProvider, Exchange, KlineType, Mode, OrderSide, OrderType, Symbol, TimeInForce
from xecution.models.config import OrderConfig, RuntimeConfig
from xecution.models.topic import DataTopic, KlineTopic
from xecution.utils.logger import Logger

KLINE_FUTURES = KlineTopic(klineType=KlineType.Binance_Futures, symbol=Symbol.BTCUSDT, timeframe="1h")
KLINE_SPOT = KlineTopic(klineType=KlineType.Binance_Spot, symbol=Symbol.BTCUSDT, timeframe="1m")

# Enable logging to see real-time data
class Engine(BaseEngine):
    """Base engine that initializes BinanceService and processes on_candle_closed and on_datasource_update."""
    def __init__(self, config):
        Logger(log_file="abc.log", log_level=logging.INFO)
        super().__init__(config)

    async def on_candle_closed(self, kline_topic: KlineTopic):
        """Handles closed candle data using `self.data_map[kline_topic]`."""
        # abc = await self.fetch_data_source(data_topic=DataTopic(provider=DataProvider.CRYPTOQUANT, url='btc/network-indicator/stock-to-flow?exchange=binance&window=hour'))
        # logging.info(f"{len(abc)}")
        # pd.DataFrame(abc).to_csv("testing.csv")
        # await self.get_order_book(Symbol.ETHUSDT)
        # await self.get_position_info(Symbol.BTCUSDT)
        # await self.get_wallet_balance()
        # await self.set_hedge_mode(False)
        # abc = await self.place_order(order_config=OrderConfig(
        #     market_type=KlineType.Binance_Futures,
        #     symbol=Symbol.BTCUSDT,
        #     side=OrderSide.BUY,
        #     order_type=OrderType.MARKET,
        #     quantity=0.02,
        #     price = 80000,
        #     time_in_force=TimeInForce.GTC
        # ))
        # logging.info(f"{abc}")
        # await self.set_leverage(Symbol.BTCUSDT,100)
        # await self.get_current_price(Symbol.BTCUSDT)
        candles = self.data_map[kline_topic]
        logging.info(f"Candle Incoming: {kline_topic} and length of {len(candles)}")
        starttime = np.array(list(map(lambda c: float(c["start_time"]), candles)))       
        candle = np.array(list(map(lambda c: float(c["close"]), candles)))           
        logging.info(f"Last Kline Closed | {kline_topic.symbol}-{kline_topic.timeframe} | Close: {candle[-1]} | Time: {datetime.fromtimestamp(starttime[-1] / 1000, tz=timezone.utc)}")

    async def on_order_update(self, order):
        logging.info(f"{order}")

    async def on_datasource_update(self, datasource_topic):
        data = self.data_map[datasource_topic]
        logging.info(f"{len(data)}")
        logging.info(f"{datasource_topic} \n {data[-1]} \n {data[-2]}")

engine = Engine(
    RuntimeConfig(
        mode= Mode.Testnet,
        kline_topic=[
            # KLINE_SPOT,
            KLINE_FUTURES
        ],
        datasource_topic=[
            DataTopic(provider=DataProvider.CRYPTOQUANT, url='/btc/market-data/coinbase-premium-index?window=hour&exchange=binance'),
            # DataTopic(provider=DataProvider.CRYPTOQUANT, url='/btc/market-data/funding-rates?window=hour&exchange=binance'),
            # DataTopic(provider=DataProvider.CRYPTOQUANT, url="btc/exchange-flows/reserve?exchange=binance&window=hour&exchange=binance"),
            # DataTopic(provider=DataProvider.CRYPTOQUANT, url="btc/exchange-flows/netflow?window=hour&exchange=binance"),
            # DataTopic(provider=DataProvider.CRYPTOQUANT, url="btc/exchange-flows/transactions-count?window=hour&exchange=binance"),
            # DataTopic(provider=DataProvider.CRYPTOQUANT, url="btc/exchange-flows/in-house-flow?exchange=binance&window=hour&exchange=binance"),
            # DataTopic(provider=DataProvider.CRYPTOQUANT, url="btc/flow-indicator/exchange-shutdown-index?exchange=binance&window=hour&exchange=binance"),
            # DataTopic(provider=DataProvider.CRYPTOQUANT, url="btc/flow-indicator/exchange-inflow-age-distribution?exchange=binance&window=hour&exchange=binance"),
            # DataTopic(provider=DataProvider.CRYPTOQUANT, url="btc/flow-indicator/exchange-inflow-cdd?exchange=binance&window=hour&exchange=binance"),
            # DataTopic(provider=DataProvider.CRYPTOQUANT, url="btc/flow-indicator/exchange-supply-ratio?window=hour&exchange=binance"),
            # DataTopic(provider=DataProvider.CRYPTOQUANT, url="btc/flow-indicator/miner-supply-ratio?miner=f2pool&window=hour&exchange=binance"),
            # DataTopic(provider=DataProvider.CRYPTOQUANT, url="btc/market-indicator/utxo-realized-price-age-distribution?window=hour&exchange=binance"),
            # DataTopic(provider=DataProvider.CRYPTOQUANT, url="btc/network-indicator/stock-to-flow?window=hour&exchange=binance"),
            # DataTopic(provider=DataProvider.CRYPTOQUANT, url="btc/network-indicator/nrpl?window=hour&exchange=binance"),
            # DataTopic(provider=DataProvider.CRYPTOQUANT, url="btc/network-indicator/utxo-age-distribution?window=hour&exchange=binance"),
            # DataTopic(provider=DataProvider.CRYPTOQUANT, url="btc/network-indicator/spent-output-age-distribution?window=hour&exchange=binance"),
            # DataTopic(provider=DataProvider.CRYPTOQUANT, url="btc/network-indicator/utxo-supply-distribution?window=hour&exchange=binance"),
            # DataTopic(provider=DataProvider.CRYPTOQUANT, url="btc/network-indicator/utxo-realized-supply-distribution?window=hour&exchange=binance"),
            # DataTopic(provider=DataProvider.CRYPTOQUANT, url="btc/network-indicator/utxo-count-supply-distribution?window=hour&exchange=binance"),
            # DataTopic(provider=DataProvider.CRYPTOQUANT, url="btc/network-indicator/spent-output-supply-distribution?window=hour&exchange=binance"),
            # DataTopic(provider=DataProvider.CRYPTOQUANT, url="btc/miner-flows/reserve?miner=f2pool&window=hour&exchange=binance"),
            # DataTopic(provider=DataProvider.CRYPTOQUANT, url="btc/miner-flows/netflow?miner=f2pool&window=hour&exchange=binance"),
            # DataTopic(provider=DataProvider.CRYPTOQUANT, url="btc/miner-flows/transactions-count?miner=f2pool&window=hour&exchange=binance"),
            # DataTopic(provider=DataProvider.CRYPTOQUANT, url="btc/miner-flows/addresses-count?miner=f2pool&window=hour&exchange=binance"),
            # DataTopic(provider=DataProvider.CRYPTOQUANT, url="btc/miner-flows/in-house-flow?miner=f2pool&window=hour&exchange=binance"),
            # DataTopic(provider=DataProvider.CRYPTOQUANT, url="btc/inter-entity-flows/exchange-to-exchange?from_exchange=binance&to_exchange=bithumb&window=hour&exchange=binance"),
            # DataTopic(provider=DataProvider.CRYPTOQUANT, url="btc/inter-entity-flows/miner-to-exchange?from_miner=f2pool&to_exchange=binance&window=hour&exchange=binance"),
            # DataTopic(provider=DataProvider.CRYPTOQUANT, url="btc/inter-entity-flows/bank-to-exchange?from_bank=blockfi&to_exchange=binance&window=hour&exchange=binance"),
            # DataTopic(provider=DataProvider.CRYPTOQUANT, url="btc/inter-entity-flows/exchange-to-miner?from_exchange=binance&to_miner=f2pool&window=hour&exchange=binance"),
            # DataTopic(provider=DataProvider.CRYPTOQUANT, url="btc/inter-entity-flows/miner-to-miner?from_miner=f2pool&to_miner=antpool&window=hour&exchange=binance"),
            # DataTopic(provider=DataProvider.CRYPTOQUANT, url="btc/inter-entity-flows/bank-to-miner?from_bank=blockfi&to_miner=f2pool&window=hour&exchange=binance"),
            # DataTopic(provider=DataProvider.CRYPTOQUANT, url="btc/inter-entity-flows/exchange-to-bank?from_exchange=binance&to_bank=blockfi&window=hour&exchange=binance"),
            # DataTopic(provider=DataProvider.CRYPTOQUANT, url="btc/market-data/taker-buy-sell-stats?window=hour&exchange=binance"),
            # DataTopic(provider=DataProvider.CRYPTOQUANT, url="btc/market-data/liquidations?window=hour&exchange=binance"),
            # DataTopic(provider=DataProvider.CRYPTOQUANT, url="btc/network-data/supply?window=hour"),
            # DataTopic(provider=DataProvider.CRYPTOQUANT, url="btc/network-data/velocity?window=hour"),
            # DataTopic(provider=DataProvider.CRYPTOQUANT, url="btc/network-data/transactions-count?window=hour"),
            # DataTopic(provider=DataProvider.CRYPTOQUANT, url="btc/network-data/addresses-count?window=hour"),
            # DataTopic(provider=DataProvider.CRYPTOQUANT, url="btc/network-data/tokens-transferred?window=hour"),
            # DataTopic(provider=DataProvider.CRYPTOQUANT, url="btc/network-data/block-bytes?window=hour"),
            # DataTopic(provider=DataProvider.CRYPTOQUANT, url="btc/network-data/block-count?window=hour"),
            # DataTopic(provider=DataProvider.CRYPTOQUANT, url="btc/network-data/block-interval?window=hour"),
            # DataTopic(provider=DataProvider.CRYPTOQUANT, url="btc/network-data/utxo-count?window=hour"),
            # DataTopic(provider=DataProvider.CRYPTOQUANT, url="btc/network-data/fees?window=hour"),
            # DataTopic(provider=DataProvider.CRYPTOQUANT, url="btc/network-data/fees-transaction?window=hour"),
            # DataTopic(provider=DataProvider.CRYPTOQUANT, url="btc/network-data/blockreward?window=hour"),
            # DataTopic(provider=DataProvider.CRYPTOQUANT, url="btc/network-data/difficulty?window=hour"),
            # DataTopic(provider=DataProvider.CRYPTOQUANT, url="btc/network-data/hashrate?window=hour"),
        ],
        data_count=10000,
        exchange=Exchange.Binance,
        API_Key="0023f3dd37d75912abffc7a7bb95def2f7a1e924dc99b2a71814ada35b59dd15" ,  # Replace with your API Key if needed
        API_Secret="5022988215bffb0a626844e7b73125533d1776b723a2abe2a8d2f8440da378d9", # Replace with your API Secret if needed
        cryptoquant_api_key="iG48lac3kRFcFq0q5WMm0BpnTt1XYMvRB6yz63OP"
    )
)

asyncio.run(engine.start())
