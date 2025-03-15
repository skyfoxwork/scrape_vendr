import os
from dotenv import load_dotenv


load_dotenv()


class Settings:
    PROJECT_NAME: str = "scrape_vendr"

    # Postgres settings
    POSTGRES_DB_NAME: str = os.getenv("POSTGRES_DB_NAME")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST")
    POSTGRES_DB_PORT: str = os.getenv("POSTGRES_DB_PORT")
    DB_CONFIG: dict = {
        "dbname": POSTGRES_DB_NAME,
        "user": POSTGRES_USER,
        "password": POSTGRES_PASSWORD,
        "host": POSTGRES_HOST,
        "port": POSTGRES_DB_PORT
    }

    TABLE_NAME: str = "products_new"

    # URL settings
    URL: str = "https://www.vendr.com/"
    URL_DEVOPS: str = "https://www.vendr.com/categories/devops"
    URL_IT_INFRASTRUCTURE: str = (
        "https://www.vendr.com/categories/it-infrastructure"
    )
    URL_DATA_ANALYTICS_MANAGEMENT: str = (
        "https://www.vendr.com/categories/data-analytics-and-management"
    )

    URLS_TO_SCRAPE: dict = {
        "devops": URL_DEVOPS,
        "it_infrastructure": URL_IT_INFRASTRUCTURE,
        "data_analytics_management": URL_DATA_ANALYTICS_MANAGEMENT
    }

    # Logging settings
    LOGGING_DEBUG: bool = False
    LOGGING_FILE_NAME: str = f"{PROJECT_NAME}.log"
    LOGGING_WRITE_TO_FILE: bool = False
    LOGGING_PRINT_TO_SCREEN: bool = True

    NUMBER_OF_THREADS: int = 100


settings = Settings()
