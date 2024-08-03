import sqlalchemy
from sqlalchemy import Engine

from config import db_config


def create_postgres_engine_from_config(config=None) -> Engine:
    if config is None:
        config = db_config.open_config()
    user = db_config.receive_postgres_user(config)
    password = db_config.receive_postgres_password(config)
    host = db_config.receive_postgres_host(config)
    port = db_config.receive_postgres_port(config)
    database = db_config.receive_postgres_database(config)
    database_url = f'postgresql://{user}:{password}@{host}:{port}/{database}'
    return sqlalchemy.create_engine(database_url)
