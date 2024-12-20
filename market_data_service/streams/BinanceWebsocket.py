import asyncio
import json
import pandas as pd
import websockets
from binance.client import Client
import psycopg2
from .BaseWebsocket import BaseDatabase
from typing import Dict, Optional
import logging

class BinanceWebsocket(BaseDatabase):
    def __init__(self):
        super().__init__()
        self.client = Client()
        self.stream_these = self._generate_stream_list()

    def _generate_stream_list(self):
        dict_ = self.client.get_exchange_info()

        symbols = [i['symbol'] for i in dict_['symbols'] if i['symbol'].endswith('USDT')]
        logging.info(f"Number of symbols: {len(symbols)}")

        return "/".join([i.lower() + '@kline_1m' for i in symbols])

    async def connect_to_websocket(self) -> str:
        while True:
            try:
                async with websockets.connect("wss://stream.binance.com:9443/ws/" + self.stream_these) as websocket:
                    logging.info("Connected to Binance WebSocket.")

                    while True:
                        message = await websocket.recv()
                        await self._process_message(message)
            
            except websockets.exceptions.ConnectionClosedError as e:
                logging.critical(f"WebSocket closed {e}. Reconnecting...")
                
                await asyncio.sleep(1)
            
            except Exception as e:
                logging.critical(f"WebSocket connection error: {e}. Reconnecting...")
                await asyncio.sleep(1)

    async def _process_message(self, message: str) -> None:
        json_message = json.loads(message)
        df = self._manipulate(json_message)
        
        if df is not None:
            connection = self._get_db_connection()
            cursor = connection.cursor()

            try:
                for index, row in df.iterrows():
                    query = "INSERT INTO bin1s (time, symbol, price, qty) VALUES (%s, %s, %s, %s)"
                    record_to_insert = (index, row[1], row[0], 23)
                    cursor.execute(query, record_to_insert)

                connection.commit()  
            except psycopg2.Error as e:
                print(f"Error during insertion: {e}")
                logging.critical(f"Error during insertion: {e}")
                
            finally:
                cursor.close()
                connection.close()

    def _manipulate(self, data: Dict) -> Optional[pd.DataFrame]:
        """Transform message into a DataFrame."""
        try:
            value_dict = data['k']
            price, sym = value_dict['c'], value_dict['s']
            event_time = pd.to_datetime([data['E']], unit='ms')

            return pd.DataFrame([[price, sym]], index=event_time)
        
        except Exception as e:
            logging.critical(f" Error in data manipulation {e}")

            return None
