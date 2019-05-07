def _get_db_engine():
    from sqlalchemy import create_engine
    from sts.config import Config

    return create_engine(Config.SQLALCHEMY_DATABASE_URI)


def _get_metadata():
    from sts import models

    return models.Base.metadata


def init_db():
    from sqlalchemy_utils import database_exists, create_database

    engine = _get_db_engine()
    metadata = _get_metadata()
    if not database_exists(engine.url):
        create_database(engine.url)

    return metadata.create_all(bind=engine)


def clear_db():
    engine = _get_db_engine()
    metadata = _get_metadata()
    return (
        metadata.create_all(bind=engine),
        metadata.drop_all(bind=engine)
    )


if __name__ == "__main__":
    import sys

    func_name = sys.argv[1]
    print(globals().get(func_name)())
