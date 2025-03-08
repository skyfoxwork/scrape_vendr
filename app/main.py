import httpx
import psycopg2
import time
import os

from parser import parce_save_products
from database import create_database
from settings import URLS_TO_SCRAPE, DB_CONFIG, TABLE_NAME


def main() -> None:
    with psycopg2.connect(**DB_CONFIG) as conn:
        create_database(conn)
        print(f"Database: ({os.getenv("POSTGRES_DB_NAME")}) created with table name: ({TABLE_NAME})")

        with httpx.Client(timeout=60) as client:
            for name, url in URLS_TO_SCRAPE.items():
                print(">>>", name, url)
                parce_save_products(client, url, conn)


if __name__ == "__main__":
    start = time.time()
    main()
    print("run time: ", time.time() - start)
