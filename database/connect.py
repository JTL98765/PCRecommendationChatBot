import psycopg2
from database.config import load_config

# Manages connection to PostgreSQL server. Returns connection to calling application
def connect(config):
    try:
        with psycopg2.connect(**config) as conn:
            print('Connected to the PostgreSQL server.')
            return conn
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)

if __name__ == '__main__':
    config = load_config()
    connect(config)