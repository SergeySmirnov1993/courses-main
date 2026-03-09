import os
import sys
import time


def wait_for_db(max_retries: int = 30, delay: int = 2) -> None:
    import psycopg2
    from psycopg2 import OperationalError

    db_config = {
        'host': os.environ.get('POSTGRES_HOST', 'db'),
        'port': os.environ.get('POSTGRES_PORT', 5432),
        'database': os.environ.get('POSTGRES_DB', 'courses_db'),
        'user': os.environ.get('POSTGRES_USER', 'courses_user'),
        'password': os.environ.get('POSTGRES_PASSWORD', 'courses_password'),
    }

    for attempt in range(max_retries):
        try:
            conn = psycopg2.connect(**db_config)
            conn.close()
            print("PostgreSQL готово")
            return True
        except OperationalError as e:
            print(f"Попытка {attempt + 1} из {max_retries}... Ошибка: {e}")
            time.sleep(delay)

    print("Не удалось подключиться к PostgreSQL")
    return False


if __name__ == "__main__":
    if wait_for_db():
        sys.exit(0)
    sys.exit(1)
