import time
from xecution.common.enums import Symbol
from xecution.models.position import Position, PositionData

class Standardize:

    @staticmethod
    def parse_binance_position(raw_data) -> Position:
        """
        假設 Binance Futures 使用 Hedge Mode 回傳的 raw_data 為一個 list，
        每個元素包含：
          - symbol: 如 "BTCUSDT"
          - positionSide: "LONG" 或 "SHORT"
          - positionAmt: 字串數字（LONG 為正、SHORT 為負）
          - entryPrice: 字串數字
          - updateTime: 時間戳（整數）
          
        這裡將同一側（LONG/SHORT）的資料累加，計算總數量及加權平均價格。
        """
        total_long_qty = 0.0
        total_long_value = 0.0
        total_short_qty = 0.0
        total_short_value = 0.0
        updated_time = 0
        symbol_str = None
        
        for item in raw_data:
            if not symbol_str:
                symbol_str = item.get("symbol")
            ts = int(item.get("updateTime", time.time() * 1000))
            updated_time = max(updated_time, ts)
            
            qty = float(item.get("positionAmt", "0"))
            entry = float(item.get("entryPrice", "0"))
            
            if qty > 0:
                total_long_qty += qty
                total_long_value += entry * qty
            elif qty < 0:
                # SHORT 的 positionAmt 通常為負數，這裡取絕對值累加
                total_short_qty += abs(qty)
                total_short_value += entry * abs(qty)
        
        if total_long_qty > 0:
            avg_long = total_long_value / total_long_qty
            long_data = PositionData(quantity=total_long_qty, avg_price=avg_long)
        else:
            long_data = PositionData(quantity=0.0, avg_price=0.0)
            
        if total_short_qty > 0:
            avg_short = total_short_value / total_short_qty
            short_data = PositionData(quantity=total_short_qty, avg_price=avg_short)
        else:
            short_data = PositionData(quantity=0.0, avg_price=0.0)
            
        if symbol_str not in Symbol._value2member_map_:
            raise ValueError(f"Unknown symbol from Binance data: {symbol_str}")
            
        return Position(
            symbol=Symbol(symbol_str),
            long=long_data,
            short=short_data,
            updated_time=updated_time or int(time.time() * 1000)
        )

    @staticmethod
    def parse_bybit_position(raw_data) -> Position:
        """
        假設 Bybit 回傳的持倉資料為一個 list，每筆資料包含：
          - symbol: 如 "BTCUSDT"
          - side: "Buy" 表示多單，"Sell" 表示空單
          - size: 持倉數量（字串數字）
          - avgEntryPrice: 平均進場價格（字串數字）
          - updateTime: (可選) 更新時間
          
        將同一側的數據累加後返回。
        """
        total_long_qty = 0.0
        total_long_value = 0.0
        total_short_qty = 0.0
        total_short_value = 0.0
        updated_time = 0
        symbol_str = None
        
        for item in raw_data:
            if not symbol_str:
                symbol_str = item.get("symbol")
            if "updateTime" in item:
                ts = int(item.get("updateTime"))
                updated_time = max(updated_time, ts)
            side = item.get("side", "").upper()
            qty = float(item.get("size", "0"))
            entry = float(item.get("avgEntryPrice", "0"))
            if side == "BUY":
                total_long_qty += qty
                total_long_value += entry * qty
            elif side == "SELL":
                total_short_qty += qty  # 假設 size 為正數表示賣出
                total_short_value += entry * qty
        
        if total_long_qty > 0:
            avg_long = total_long_value / total_long_qty
            long_data = PositionData(quantity=total_long_qty, avg_price=avg_long)
        else:
            long_data = PositionData(quantity=0.0, avg_price=0.0)
            
        if total_short_qty > 0:
            avg_short = total_short_value / total_short_qty
            short_data = PositionData(quantity=total_short_qty, avg_price=avg_short)
        else:
            short_data = PositionData(quantity=0.0, avg_price=0.0)
            
        if symbol_str not in Symbol._value2member_map_:
            raise ValueError(f"Unknown symbol from Bybit data: {symbol_str}")
        
        return Position(
            symbol=Symbol(symbol_str),
            long=long_data,
            short=short_data,
            updated_time=updated_time or int(time.time() * 1000)
        )

    @staticmethod
    def parse_okx_position(raw_data) -> Position:
        """
        假設 OKX 回傳的持倉資料為一個 dict，包含：
          - instId: 如 "BTC-USDT"，需轉換為 "BTCUSDT"
          - longQty: 多單數量（字串數字）
          - longAvgPx: 多單平均價格（字串數字）
          - shortQty: 空單數量（字串數字）
          - shortAvgPx: 空單平均價格（字串數字）
          - ts: 更新時間（字串或數字）
        直接解析並返回 Position。
        """
        inst_id = raw_data.get("instId", "")
        symbol_str = inst_id.replace("-", "")
        updated_time = int(raw_data.get("ts", time.time() * 1000))
        long_qty = float(raw_data.get("longQty", "0"))
        long_avg = float(raw_data.get("longAvgPx", "0"))
        short_qty = float(raw_data.get("shortQty", "0"))
        short_avg = float(raw_data.get("shortAvgPx", "0"))
        if symbol_str not in Symbol._value2member_map_:
            raise ValueError(f"Unknown symbol from OKX data: {symbol_str}")
        return Position(
            symbol=Symbol(symbol_str),
            long=PositionData(quantity=long_qty, avg_price=long_avg),
            short=PositionData(quantity=short_qty, avg_price=short_avg),
            updated_time=updated_time
        )
