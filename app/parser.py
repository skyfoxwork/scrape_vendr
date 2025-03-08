import queue
import threading
from dataclasses import dataclass

import httpx
from bs4 import BeautifulSoup

from database import save_to_db
from settings import URL


@dataclass
class Product:
    product_name: str
    category: str | None
    price_range: dict | None
    description: str | None


def parse_single_product(product: BeautifulSoup, category_name: str) -> Product:
    price_range = None
    price = product.find("div", "rt-Flex rt-r-fd-column xs:rt-r-fd-row xs:rt-r-ai-center xs:rt-r-jc-space-between rt-r-gap-5")

    if price:
        low = product.find("span", "v-fw-600 v-fs-12")
        medium = product.find("div", "rt-Flex _rangeAverage_118fo_42")
        height = product.find("span", "_rangeSliderLastNumber_118fo_38 v-fw-600 v-fs-12")
        price_range = {
            "low": low.text.split("$")[-1] if low else None,
            "medium": medium.text.split("$")[-1] if medium else None,
            "height": height.text.split("$")[-1] if height else None
        }

    product_name = product.find("h1")
    description = product.find("p", "rt-Text")
    return Product(
        product_name=product_name.text if product_name else None,
        category=category_name,
        price_range=price_range,
        description=description.text if description else None
    )


def send_request_get_product_links(
        count: int,
        page: int,
        category: str,
        client: httpx.Client,
        all_product_urls: list
):
    # print(f"Sending request: {count}")
    next_url = list(category)
    next_url[-1] = str(page)
    response = client.get("".join(next_url))
    text = response.content
    soup = BeautifulSoup(text, "html.parser")
    links = soup.find_all("a", "_card_j928a_9 _card_1u7u9_1 _cardLink_1q928_1")
    product_urls = [URL + link.get("href")[1:] for link in links]
    all_product_urls += product_urls
    # print(f"got response for request {count}, status code {response.status_code}")


def send_request_parce_single_product(
        count: int,
        url: str,
        client: httpx.Client,
        data_queue: queue.Queue,
        category_name: str
):
    # print(f"Sending request: {count}")
    response = client.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    data_queue.put(parse_single_product(soup, category_name))
    # print(f"got response for request {count}, status code {response.status_code}")


# thread that sava data to db
def save_data(data_queue, db_connection) -> None:
    while True:
        data = data_queue.get()
        if data is None:
            print("Received termination signal, stopping thread.")
            data_queue.task_done()
            break

        # print(f"Saving to DB: {data.product_name}")
        save_to_db(data, db_connection)
        data_queue.task_done()


def parce_save_products(client: httpx.Client, url: str, db_connection) -> list[Product]:
    response = client.get(url)

    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all("a", "rt-Text rt-reset rt-Link rt-r-size-2 rt-underline-auto")
    category_urls = [URL + link.get("href")[1:] for link in links]
    # print(category_urls)

    for category in category_urls: # [2:3] [3:4]
        print("category:", category)

        text = client.get(category).content
        soup = BeautifulSoup(text, "html.parser")

        # find product category name
        category_name = soup.find("h1", "rt-Heading rt-r-size-6").text
        print("category name:", category_name)

        # find all product urls first page
        all_product_urls = []
        links = soup.find_all("a", "_card_j928a_9 _card_1u7u9_1 _cardLink_1q928_1")
        product_urls = [URL + link.get("href")[1:] for link in links]
        all_product_urls += product_urls

        # find number of pages
        prev_button = soup.find("button", {"aria-label": "Previous page"})
        if prev_button:
            page_info = prev_button.find_next_sibling("span")
            if page_info:
                number_of_pages = int(page_info.text.split()[-1])
                print("number of pages:", number_of_pages)

        # find all product url on other pages
        task_all_product = []
        for i, page in enumerate(range(2, number_of_pages + 1)):
            task_all_product.append(
                threading.Thread(
                    target=send_request_get_product_links,
                    args=(i, page, category, client, all_product_urls))
            )
            task_all_product[-1].start()

        for task in task_all_product:
            task.join()

        # print(all_product_urls)
        print("number of products:", len(all_product_urls))
        print("parsing process ...")

        # find, parce and write products to db
        data_queue = queue.Queue()
        tasks = []

        # write product to db thread run
        db_thread = threading.Thread(target=save_data, args=(data_queue, db_connection))
        db_thread.start()

        # parse products threads run
        for i, product_url in enumerate(all_product_urls):
            tasks.append(
                threading.Thread(
                    target=send_request_parce_single_product,
                    args=(i, product_url, client, data_queue, category_name)
                )
            )
            tasks[-1].start()

        for task in tasks:
            task.join()

        # stop write product to db thread
        print("put None")
        data_queue.put(None)
        db_thread.join()
