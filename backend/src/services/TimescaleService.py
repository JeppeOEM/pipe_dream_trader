
import datetime
import psycopg2
from config import Config

class TimescaleService:
    def __init__(self):
        self.db_url = Config.TIMESCALE_DATABASE_URL

    def get_connection(self):
        return psycopg2.connect(self.db_url)

    def execute_raw_sql(self, query: str):
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query)
                conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Error executing query: {e}")
        finally:
            conn.close()

    def refresh_materialized_views(self):
        now = datetime.datetime.now()
        print(f"Current minute: {now.minute}")

        if now.minute % 5 == 0:
            self.execute_raw_sql("REFRESH MATERIALIZED VIEW ohlc_data_1minute;")
            self.execute_raw_sql("REFRESH MATERIALIZED VIEW ohlc_data_5minute;")
        else:
            self.execute_raw_sql("REFRESH MATERIALIZED VIEW ohlc_data_1minute;")
        

