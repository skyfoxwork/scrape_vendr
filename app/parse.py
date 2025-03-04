import csv
import time
from dataclasses import dataclass, fields, astuple

import requests
from bs4 import BeautifulSoup

URL = "https://www.vendr.com/"
URL_DEVOPS = "https://www.vendr.com/categories/devops"
URL_IT_INFRASTRUCTURE = "https://www.vendr.com/categories/it-infrastructure"
URL_DATA_ANALYTICS_MANAGEMENT = "https://www.vendr.com/categories/data-analytics-and-management"


@dataclass
class Product:
    product_name: str
    category: str | None
    price_range: dict | None
    description: str | None

PRODUCT_FIELDS = [field.name for field in fields(Product)]


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


def get_products() -> list[Product]:
    text = requests.get(URL_DEVOPS).content
    soup = BeautifulSoup(text, "html.parser")
    links = soup.find_all("a", "rt-Text rt-reset rt-Link rt-r-size-2 rt-underline-auto")

    categories_urls = [URL + link.get("href")[1:] for link in links]
    # print(categories_urls[0])
    # print(len(links))

    product_data = []
    for category in categories_urls:
        print("category:", category)

        text = requests.get(category).content
        soup = BeautifulSoup(text, "html.parser")

        # find product category name
        category_name = soup.find("h1", "rt-Heading rt-r-size-6").text
        print("category_name:", category_name)

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
                print("number_of_pages:", number_of_pages)

        # find all product next page urls
        for page in range(2, number_of_pages + 1):
            next_url = list(category)
            next_url[-1] = str(page)
            text = requests.get("".join(next_url)).content
            soup = BeautifulSoup(text, "html.parser")
            links = soup.find_all("a", "_card_j928a_9 _card_1u7u9_1 _cardLink_1q928_1")
            product_urls = [URL + link.get("href")[1:] for link in links]
            all_product_urls += product_urls

        # print(all_product_urls)
        print("number of products:", len(all_product_urls))

        i = 1
        for product_url in all_product_urls:
            print(i, product_url)
            product = requests.get(product_url).content
            soup = BeautifulSoup(product, "html.parser")
            product_data.append(parse_single_product(soup, category_name))
            i += 1

    # print(product_data)
    return product_data


def main(output_csv_path: str) -> None:
    products = get_products()
    with open(f"{output_csv_path}", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(PRODUCT_FIELDS)
        writer.writerows([astuple(product) for product in products])


if __name__ == "__main__":
    start = time.time()
    main("products_sample.csv")
    print("run time: ", time.time() - start)
