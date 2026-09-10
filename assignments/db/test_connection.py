import psycopg
import os
import time
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

start = time.perf_counter()

with psycopg.connect(DATABASE_URL) as con:
    print("CONNECTED:", time.perf_counter() - start)

    start = time.perf_counter()

    with con.cursor() as cur:
        cur.execute("SELECT 1")
        print("QUERY:", time.perf_counter() - start)