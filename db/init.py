from db.connection import create_postgres_engine_from_config
from db.models import Base


def create_tables_if_not_exist(config=None):
    engine = create_postgres_engine_from_config(config)
    Base.metadata.create_all(engine)


if __name__ == '__main__':
    create_tables_if_not_exist()
