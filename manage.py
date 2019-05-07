import sys

from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

from sts.config import Config
from sts import models


def _get_db_engine():
    return create_engine(Config.SQLALCHEMY_DATABASE_URI)


def _get_metadata():
    return models.Base.metadata


def init_db():
    engine = _get_db_engine()
    metadata = _get_metadata()
    if not database_exists(engine.url):
        create_database(engine.url)

    return metadata.create_all(bind=engine)


def clear_db():
    engine = _get_db_engine()
    metadata = _get_metadata()
    return (metadata.drop_all(bind=engine), metadata.create_all(bind=engine))


if __name__ == "__main__":
    func_name = sys.argv[1]
    print(globals().get(func_name)())
