# TODO: this is a temporary solution, it should be replaced with a proper config file
POSTGRESQL_USER = "postgres"
POSTGRESQL_PASSWORD = "postgres"
POSTGRESQL_HOST = "localhost"
POSTGRESQL_PORT = "2345"
POSTGRESQL_DATABASE = "test"
POSTGRESQL_DATABASE_URI = f"postgresql://{POSTGRESQL_USER}:{POSTGRESQL_PASSWORD}@{POSTGRESQL_HOST}:{POSTGRESQL_PORT}/{POSTGRESQL_DATABASE}"
