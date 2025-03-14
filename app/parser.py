import queue
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

import httpx
from bs4 import BeautifulSoup

from database import save_to_db
from config import settings


@dataclass
class Product:
    product_name: str
    category: str | None
    price_range: dict | None
    description: str | None


def parse_single_product(
        product: BeautifulSoup,
        category_name: str
) -> Product:
    """
    This function parse single product, write it to Product dataclass
    and return Product dataclass
    """
    price_range = None
    price = product.find(
        "div",
        (
            "rt-Flex rt-r-fd-column xs:rt-r-fd-row xs:"
            "rt-r-ai-center xs:rt-r-jc-space-between rt-r-gap-5"
        )
    )

    if price:
        low = product.find("span", "v-fw-600 v-fs-12")
        medium = product.find("div", "rt-Flex _rangeAverage_118fo_42")
        height = product.find(
            "span", "_rangeSliderLastNumber_118fo_38 v-fw-600 v-fs-12"
        )
        price_range = {
            "low": low.text.split("$")[-1] if low else None,
            "medium": medium.text.split("$")[-1] if medium else None,
            "high": height.text.split("$")[-1] if height else None
        }

    product_name = product.find("h1")
    description = product.find("p", "rt-Text")
    return Product(
        product_name=product_name.text if product_name else None,
        category=category_name,
        price_range=price_range if price else None,
        description=description.text if description else None
    )


def send_request_get_product_links(
        page: int,
        category: str,
        client: httpx.Client,
        all_product_urls: list
) -> None:
    """
    This function is a thread that send request,
    get product links and save links to list for page
    """
    next_url = list(category)
    next_url[-1] = str(page)
    response = client.get("".join(next_url))
    text = response.content
    soup = BeautifulSoup(text, "html.parser")
    links = soup.find_all("a", "_card_j928a_9 _card_1u7u9_1 _cardLink_1q928_1")
    product_urls = [settings.URL + link.get("href")[1:] for link in links]
    all_product_urls += product_urls


def send_request_parse_single_product(
        url: str,
        client: httpx.Client,
        data_queue: queue.Queue,
        category_name: str
):
    """
    This function is a thread that send request,
    parse single product and write it to queue.Queues
    """
    print("send request")
    response = client.get(url)
    print("received response")
    soup = BeautifulSoup(response.content, "html.parser")
    data_queue.put(parse_single_product(soup, category_name))


def save_data(data_queue: queue.Queue, db_connection) -> None:
    """
    This function is a thread that get Product from queue.Queue,
    save it to database
    and exits the thread if None is the last one in queue.Queue
    """
    while True:
        data = data_queue.get()
        if data is None:
            data_queue.task_done()
            break

        print("save to db")
        save_to_db(data, db_connection)
        data_queue.task_done()


def get_product_urls(
        category: str, soup: BeautifulSoup, client: httpx.Client
) -> list:
    """
    This function find product urls on first page and
    create Threads to find product urls on other pages
    and return product urls
    """

    # find product urls first page
    all_product_urls = []
    links = soup.find_all("a", "_card_j928a_9 _card_1u7u9_1 _cardLink_1q928_1")
    product_urls = [settings.URL + link.get("href")[1:] for link in links]
    all_product_urls += product_urls

    # find number of pages
    prev_button = soup.find("button", {"aria-label": "Previous page"})
    if prev_button:
        page_info = prev_button.find_next_sibling("span")
        if page_info:
            number_of_pages = int(page_info.text.split()[-1])
            print("number of pages:", number_of_pages)

    # parse product urls threads run with max number of threads
    with ThreadPoolExecutor(
            max_workers=settings.NUMBER_OF_THREADS
    ) as executor:
        for page in range(2, number_of_pages + 1):
            executor.submit(
                send_request_get_product_links,
                page, category, client, all_product_urls
            )

    return all_product_urls


def parse_save_to_db_product_data(
        all_product_urls: list,
        client: httpx.Client,
        db_connection,
        category_name: str
) -> None:
    """
    This function take products urls, create threads to parse products urls
    and create one thread to save Products to database

    use queue.Queue() for threading communication
    all thread put Products to data_queue
    one thread get Products from data_queue and save Product ot database
    """

    data_queue = queue.Queue()

    # write product to db thread run
    db_thread = threading.Thread(
        target=save_data,
        args=(data_queue, db_connection)
    )
    db_thread.start()

    # parse products threads run with max number of threads
    with ThreadPoolExecutor(
            max_workers=settings.NUMBER_OF_THREADS
    ) as executor:
        for product_url in all_product_urls:
            executor.submit(
                send_request_parse_single_product,
                product_url, client, data_queue, category_name
            )

    # stop thread that write product to db
    data_queue.put(None)
    db_thread.join()


def parse_save_products(
        client: httpx.Client,
        url: str,
        db_connection
) -> list[Product]:
    """
    The main function that parse one product link and save product to database
    For example: DevOps, It infrastructure or data analytics management product
    """

    # find category urls
    response = client.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all(
        "a", "rt-Text rt-reset rt-Link rt-r-size-2 rt-underline-auto"
    )
    category_urls = [settings.URL + link.get("href")[1:] for link in links]

    # parse categories
    for category in category_urls:
        text = client.get(category).content
        soup = BeautifulSoup(text, "html.parser")

        category_name = soup.find("h1", "rt-Heading rt-r-size-6").text
        print("category name:", category_name)
        print("category url:", category)

        product_urls = get_product_urls(category, soup, client)
        print("number of products:", len(product_urls))
        print("parsing process ...")

        parse_save_to_db_product_data(
            product_urls, client, db_connection, category_name
        )
        print("Done", "\n")
