import os
from dotenv import load_dotenv


load_dotenv()  # take environment variables from .env.


DB_CONFIG = {
    "dbname": os.getenv("POSTGRES_DB_NAME"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "host": os.getenv("POSTGRES_HOST"),
    "port": os.getenv("POSTGRES_DB_PORT")
}


TABLE_NAME = "products_six"

# main url
URL = "https://www.vendr.com/"

# url to scrape
URL_DEVOPS = "https://www.vendr.com/categories/devops"
URL_IT_INFRASTRUCTURE = "https://www.vendr.com/categories/it-infrastructure"
URL_DATA_ANALYTICS_MANAGEMENT = "https://www.vendr.com/categories/data-analytics-and-management"


URLS_TO_SCRAPE = {
    "devops": URL_DEVOPS,
    "it_infrastructure": URL_IT_INFRASTRUCTURE,
    "data_analytics_management": URL_DATA_ANALYTICS_MANAGEMENT
}
