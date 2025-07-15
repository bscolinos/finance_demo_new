import os
import time
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import singlestoredb as s2
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from dotenv import load_dotenv

load_dotenv(override=True)

THROUGHPUT = 10
MODE = os.getenv("MODE", "db")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "10"))
NUM_THREADS = int(os.getenv("NUM_THREADS", "8"))
LOG_INTERVAL = int(os.getenv("LOG_INTERVAL", "5"))

config = {
    "host": os.getenv('host'),
    "port": os.getenv('port'),
    "user": os.getenv('user'),
    "password": os.getenv('password'),
    "database": os.getenv('database')
}

def create_rate_limiter(rate_per_second):
    interval = 1.0 / rate_per_second
    next_time = [time.monotonic()]
    def limiter():
        now = time.monotonic()
        if now < next_time[0]:
            time.sleep(next_time[0] - now)
        next_time[0] = time.monotonic() + interval
    return limiter

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=1, max=5),
       retry=retry_if_exception_type(Exception))
def insert_trades(trades, config):
    if not trades:
        return
    query = """
    INSERT INTO live_trades
    (localTS, localDate, ticker, conditions, correction, exchange, id, participant_timestamp,
     price, sequence_number, sip_timestamp, size, tape, trf_id, trf_timestamp)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    # Order the keys exactly as they appear in the query.
    columns_order = [
        "localTS", "localDate", "ticker", "conditions", "correction", "exchange",
        "id", "participant_timestamp", "price", "sequence_number", "sip_timestamp",
        "size", "tape", "trf_id", "trf_timestamp"
    ]
    # Convert the list of dictionaries into list of tuples.
    trades_tuples = [tuple(trade[col] for col in columns_order) for trade in trades]
    conn = s2.connect(**config)
    cur = conn.cursor()
    try:
        cur.executemany(query, trades_tuples)
        conn.commit()
    except Exception as e:
        print("Error during DB insert:", e)
        raise
    finally:
        cur.close()
        conn.close()

def produce_batch(trades, mode, config):
    if mode == "db":
        insert_trades(trades, config)
    else:
        print(f"Simulated insertion of {len(trades)} trades.")

def load_data():
    df = pd.read_csv('trades_data.csv')
    required_cols = [
        "localTS", "localDate", "ticker", "conditions", "correction", "exchange",
        "id", "participant_timestamp", "price", "sequence_number", "sip_timestamp",
        "size", "tape", "trf_id", "trf_timestamp"
    ]
    for col in required_cols:
        if col not in df.columns:
            df[col] = 0
    df['conditions'] = df['conditions'].fillna('').astype(str)
    return df

def simulate_trades(throughput, mode, batch_size, num_threads, config):
    df = load_data()
    total_trades = 0
    rate_limiter = create_rate_limiter(throughput)
    last_log_time = time.time()

    def send_batch(trades):
        produce_batch(trades, mode, config)
        return len(trades)

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []
        try:
            while True:
                batch = df.sample(n=batch_size, replace=True).copy()
                current_dt = datetime.now()
                current_ts_str = current_dt.strftime("%Y-%m-%d %H:%M:%S")
                current_date_str = current_dt.strftime("%Y-%m-%d")
                current_ts_ns = int(current_dt.timestamp() * 1e9)

                batch['localTS'] = current_ts_str
                batch['localDate'] = current_date_str
                batch['participant_timestamp'] = current_ts_ns
                batch['sip_timestamp'] = current_ts_ns
                batch['trf_timestamp'] = current_ts_ns

                trades_list = batch.to_dict(orient='records')
                rate_limiter()
                futures.append(executor.submit(send_batch, trades_list))

                now = time.time()
                if now - last_log_time > LOG_INTERVAL:
                    last_log_time = now

                for f in list(futures):
                    if f.done():
                        total_trades += f.result()
                        futures.remove(f)
        except KeyboardInterrupt:
            pass
        finally:
            print(f"Simulation ended. Total trades sent: {total_trades}")

def main():
    print("Starting trade simulation...")
    simulate_trades(throughput=THROUGHPUT, mode=MODE, batch_size=BATCH_SIZE,
                    num_threads=NUM_THREADS, config=config)
    print("Trade simulation complete.")

if __name__ == '__main__':
    main()