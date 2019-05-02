def db_init():
    # from sts.app import app, db

    from sqlalchemy import create_engine

    from sts import models
    from sts.config import Config
    # app = create_app()
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)


    models.Base.metadata.create_all(bind=engine)

    # if you have more models just add them here
    # from project.models.model2 import Model2
    # from project.models.lots_of_models import Model3, Model4, Model5

    # db.create_all()


if __name__ == "__main__":
    db_init()
