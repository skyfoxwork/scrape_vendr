# "df_scrap"

Python project that scrapes product data from specific categories on the website [Vendr](https://www.vendr.com/),
parses relevant information about each product, and saves it into a PostgreSQL database.

## Description
The project:
- collect data: product name, category, price range, and description. 
- implement a task queue specifically for managing the product scraping. Each thread take a task (i.e., a product to scrape) from the queue and process it.  
- use multithreading, when multiple threads fetching product data from the queue and one dedicated thread writing the collected data to the database in parallel. 


## Project Structure
```
df_scrape/
├── app/
│   ├── database.py          # Contains functions to create the database and save data
│   ├── parser.py            # Contains parsing logic for product data
│   ├── settings.py          # Configuration file with database and URL settings
│   ├── main.py              # Main script to execute the scraping and saving
├── .env                     # Environment variables for sensitive data (e.g., DB credentials)
├── requirements.txt         # List of Python dependencies
└── README.md                # Project documentation
```

## Technologies

- Python 3
- Postgres

## Requirements
- httpx
- threading
- BeautifulSoup4
- psycopg2
- dotenv

## Installation

1. Install Python3:

```shell
www.python.org/
```

2. Install Git:

```shell
git-scm.com/
```

3. Install postgres
```shell
www.postgresql.org
```

4. Create database (postgres)

Enter to postgres

MacOS:
```shell
psql -U postgres
```

Linux MacOS:
```shell
sudo -u postgres psql
```

create database
```shell
CREATE DATABASE <your_db_name>;
```

if you need create user
```shell
CREATE USER <your_db_user> WITH PASSWORD <your_db_password>;

```

The script automatically creates a database table (default name: products) to store the product data. Ensure that your PostgreSQL database is running before executing the script.

If you need to change default name of table change TABLE_NAME in settings.py file.

5. Clone the repository.

```shell
git clone https://github.com/skyfoxwork/df_scrap.git
```

6. Navigate to the project directory:

```shell
cd df_scrap
```

```shell
git checkout task1
```

7. Create virtual environment:

```shell
python3 -m venv venv
```

8. Activate virtual environment (venv).

MacOS, Linux:

```shell
source venv/bin/activate
```
   Windows:

```shell
venv\Scripts\activate
```

if you need to deactivate virtual environment use:

```shell
deactivate
```

9. Install dependencies:

```shell
pip install -r requirements.txt
```


10. Set Up Environment Variables
Create a .env file in the root of the project and add the following environment variables:

Create .env file
```shell
cp .env.sample .env
```

Change environment variables in .env file
```shell
POSTGRES_DB_NAME=<your_db_name>
POSTGRES_PASSWORD=<your_db_password>
POSTGRES_USER=<your_db_user>
POSTGRES_HOST=<your_db_host>
POSTGRES_DB_PORT=<your_db_port>
```

11. Run project:

```shell
python3 app/main.py
```

12. To see scraped data from database use:
```shell
python3 app/database.py
```

if you need change default settings in project use settings.py file
