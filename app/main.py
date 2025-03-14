import os
import time

import httpx
import psycopg2

from parser import parse_save_products
from database import create_database, print_total_number_of_data
from config import settings


def main() -> None:
    with psycopg2.connect(**settings.DB_CONFIG) as conn:
        create_database(conn)
        print(
            f"Database: ({os.getenv('POSTGRES_DB_NAME')}) "
            f"is created with table name: ({settings.TABLE_NAME})",
            "\n"
        )

        with httpx.Client(timeout=60) as client:
            for name, url in settings.URLS_TO_SCRAPE.items():
                print(">>>", name, url, "\n")
                parse_save_products(client, url, conn)


if __name__ == "__main__":
    start = time.time()
    main()
    print("-" * 50)
    print(
        "total number of products:",
        print_total_number_of_data(settings.TABLE_NAME)
    )
    print("run time:", time.time() - start)
