import logging
from config import settings


# create logger
logger = logging.getLogger(settings.PROJECT_NAME)

if settings.LOGGING_DEBUG:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

# format
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

# create console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# add handlers to logger
logger.addHandler(console_handler)

if settings.LOGGING_WRITE_TO_FILE:
    # create file handler
    file_handler = logging.FileHandler(
        settings.LOGGING_FILE_NAME, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    # add handlers to logger
    logger.addHandler(file_handler)
