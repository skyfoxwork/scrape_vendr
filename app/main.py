import os
import time

import httpx
import psycopg2

from parser import parse_save_products
from database import create_database, get_total_number_of_data
from config import settings
from app_logging import logger


def main() -> None:
    with psycopg2.connect(**settings.DB_CONFIG) as conn:
        create_database(conn)
        logger.info(
            f"Database: ({os.getenv('POSTGRES_DB_NAME')}) "
            f"is created with table name: ({settings.TABLE_NAME})\n"
        )

        with httpx.Client(timeout=60) as client:
            for name, url in settings.URLS_TO_SCRAPE.items():
                logger.info(f">>> {name} {url} \n")
                parse_save_products(client, url, conn)


if __name__ == "__main__":
    start = time.time()
    main()
    stop = time.time() - start
    total_number_products = get_total_number_of_data(settings.TABLE_NAME)

    logger.info("-" * 50)
    logger.info(f"total number of products: {total_number_products}")
    logger.info(f"run time: {stop}")
