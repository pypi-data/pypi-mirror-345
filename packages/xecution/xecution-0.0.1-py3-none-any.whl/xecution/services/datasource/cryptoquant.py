import json
import logging
import asyncio
import aiohttp
from datetime import datetime, timedelta, timezone
from xecution.common.datasource_constants import CryptoQuantConstants
from xecution.models.config import RuntimeConfig
from xecution.models.topic import DataTopic
from xecution.services.connection.restapi import RestAPIClient

class CryptoQuantClient:
    def __init__(self, config: RuntimeConfig, data_map: dict):
        self.config      = config
        self.rest_client = RestAPIClient()
        self.data_map    = data_map
        self.headers     = {
            'Authorization': f'Bearer {self.config.cryptoquant_api_key}',
        }

    async def fetch(self, data_topic: DataTopic, last_n: int = 3):
        """
        Fetch only the last `last_n` records for `data_topic`
        (no `to` param—just limit=last_n), store & return as list of dicts.
        """
        # parse path and base params
        if '?' in data_topic.url:
            path, qs = data_topic.url.split('?', 1)
            base_params = dict(part.split('=', 1) for part in qs.split('&'))
        else:
            path = data_topic.url
            base_params = {}

        url = CryptoQuantConstants.BASE_URL + path

        # build params: limit=last_n
        params = {**base_params, 'limit': last_n}

        # call API
        try:
            raw = await self.rest_client.request(
                method='GET',
                url=url,
                params=params,
                headers=self.headers
            )
        except Exception as e:
            logging.error(f"[{datetime.now()}] Error fetching last {last_n} for {data_topic.url}: {e}")
            return []

        # unwrap result/data
        result = raw.get('result', raw)
        data   = result.get('data') if isinstance(result, dict) else result
        if not data:
            logging.warning(f"[{datetime.now()}] No data returned for last {last_n} of {data_topic.url}")
            return []

        # normalize to list
        items = data if isinstance(data, list) else [data]

        # process items: parse timestamp
        processed = []
        for item in items:
            dt_str = item.get('datetime') or item.get('date')
            if dt_str:
                try:
                    item['start_time'] = self.parse_datetime_to_timestamp(dt_str)
                except ValueError as ex:
                    logging.warning(f"Date parsing failed ({dt_str}): {ex}")
            processed.append(item)

        # sort & take last_n
        processed.sort(key=lambda x: x.get('start_time', 0))
        final = processed[-last_n:]

        # store & return
        self.data_map[data_topic] = final
        return final

    async def fetch_all_parallel(self, data_topic: DataTopic):
        """
        Fetch in parallel up to config.data_count hourly bars ending now,
        log any missing values, forward-fill them, store in self.data_map, and return list of dicts.
        """
        limit      = self.config.data_count
        base_limit = 1000
        windows    = -(-limit // base_limit)  # ceil division
        end        = datetime.now(timezone.utc)

        # parse URL and base params
        if '?' in data_topic.url:
            path, qs = data_topic.url.split('?', 1)
            base_params = dict(part.split('=') for part in qs.split('&'))
        else:
            path = data_topic.url
            base_params = {}
        url = CryptoQuantConstants.BASE_URL + path

        async with aiohttp.ClientSession() as session:
            # each batch will use the same session and then it's auto‐closed
            async def fetch_batch(to_ts: datetime):
                from_str = to_ts.strftime('%Y%m%dT%H%M%S')
                params   = {
                    **base_params,
                    "limit": base_limit,
                    "to":    from_str,
                    "format":"json"
                }
                try:
                    async with session.get(url, params=params, headers=self.headers) as resp:
                        resp.raise_for_status()
                        raw = await resp.json()
                except Exception as e:
                    logging.error(f"[{datetime.now()}] Parallel fetch error: {e}")
                    return []

                # unwrap result/data
                result = raw.get("result", raw.get("data", raw))
                if isinstance(result, dict) and "data" in result:
                    result = result["data"]
                    if isinstance(result, str):
                        result = json.loads(result)
                if isinstance(result, dict):
                    result = [result]

                records = []
                for item in result or []:
                    dt_str = (
                        item.get("datetime")
                    )
                    if dt_str:
                        try:
                            item["start_time"] = self.parse_datetime_to_timestamp(dt_str)
                        except ValueError as ex:
                            logging.warning(f"Date parsing failed ({dt_str}): {ex}")
                            continue
                    records.append(item)
                return records

            # run parallel batches under the same session
            tasks   = [
                fetch_batch(end - timedelta(hours=i * base_limit))
                for i in range(windows)
            ]
            batches = await asyncio.gather(*tasks)

        # === session is now closed ===

        # flatten, sort, dedupe as before
        flat    = [rec for batch in batches for rec in batch if isinstance(rec, dict)]
        flat.sort(key=lambda x: x.get("start_time", 0))
        deduped = {x["start_time"]: x for x in flat if "start_time" in x}

        # ── new: subtract a small buffer to account for dropped dups ──
        buffer   = 5
        effective = max(0, limit - buffer)
        final    = list(deduped.values())[-effective:]

        # forward-fill missing values and log errors
        filled = []
        prev   = None
        for rec in final:
            if prev is not None:
                for k, v in rec.items():
                    if v is None:
                        logging.warning(
                            f"Missing value for '{k}' at start_time: {rec['start_time']},datetime: {rec['datetime']}, forward-filled"
                        )
                        rec[k] = prev.get(k)
            else:
                for k, v in rec.items():
                    if v is None:
                        logging.error(f"Missing value for '{k}' at start_time {rec['start_time']}")
            filled.append(rec)
            prev = rec

        self.data_map[data_topic] = filled
        return filled

    def parse_datetime_to_timestamp(self, dt_str: str) -> int:
        for fmt in (
            '%Y-%m-%dT%H:%M:%S.%fZ',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%d %H:%M:%S',
        ):
            try:
                dt = datetime.strptime(dt_str, fmt).replace(tzinfo=timezone.utc)
                return int(dt.timestamp() * 1000)
            except ValueError:
                continue
        try:
            clean = dt_str.rstrip('Z')
            dt    = datetime.fromisoformat(clean)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return int(dt.timestamp() * 1000)
        except Exception:
            raise ValueError(f"Unrecognized date format: {dt_str}")
