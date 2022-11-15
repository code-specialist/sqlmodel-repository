POSTGRESQL_USER = 'postgres'
POSTGRESQL_PASSWORD = 'postgres'
POSTGRESQL_HOST = 'localhost'
POSTGRESQL_PORT = '5432'
POSTGRESQL_DATABASE_URI = f'postgresql://{POSTGRESQL_USER}:{POSTGRESQL_PASSWORD}@{POSTGRESQL_HOST}:{POSTGRESQL_PORT}'

SQLITE_DATABASE_URI = 'sqlite:///test.db'  # in-memory database does not support multi-session