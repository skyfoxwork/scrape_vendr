import json
import psycopg2

from settings import DB_CONFIG, TABLE_NAME


def create_database(conn):
    cursor = conn.cursor()
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id SERIAL PRIMARY KEY,
            name TEXT,
            category TEXT,
            price_range JSONB,
            description TEXT
        )
    """)
    conn.commit()
    cursor.close()


def save_to_db(data, conn) -> None:
    cursor = conn.cursor()

    cursor.execute(f"""
        INSERT INTO {TABLE_NAME} (name, category, price_range, description)
        VALUES (%s, %s, %s, %s)
    """, (
        data.product_name,
        data.category,
        json.dumps(data.price_range),
        data.description
    ))
    conn.commit()
    cursor.close()


def print_total_number_of_data(table_name: str) -> None:
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            total_number = cursor.fetchall()[0][0]
    return total_number


def print_data(table_name: str) -> None:
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            for row in rows:
                print(row)
            print("-" * 50)
            print("total number of elements:", len(rows))


if __name__ == "__main__":
    print_data(TABLE_NAME)
