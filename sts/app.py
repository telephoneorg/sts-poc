from argparse import Namespace

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_graphql import GraphQLView
from flask_cors import CORS

from .cognito_auth import (
    CognitoAuth,
    current_user,
    current_cognito_jwt,
    load_jwt_tokens,
)
from . import schema
from . import models


app = Flask(__name__)
app.config.from_object("sts.config.Config")
db = SQLAlchemy(app, metadata=models.Base.metadata)
cogauth = CognitoAuth(app)
cors = CORS(
    app,
    supports_credentials=app.config["CORS_ALLOW_CREDENTIALS_GLOBAL"],
    origins=app.config["CORS_ORIGINS_GLOBAL"],
)


@app.before_first_request
def setup():
    models.Base.query = db.session.query_property()


app.add_url_rule(
    "/graphql",
    view_func=GraphQLView.as_view(
        "graphql",
        schema=schema.schema,
        graphiql=True,
        get_context=lambda request=None: Namespace(
            request=request,
            session=db.session,
            current_user=current_user,
            current_jwt=current_cognito_jwt,
        ),
    ),
)

app.before_request(load_jwt_tokens)


@cogauth.identity_handler
def lookup_cognito_user(payload):
    app.logger.info("jwt_payload: {}".format(payload))
    """Look up user in our database from Cognito JWT payload."""
    user = (
        db.session.query(models.User)
        .filter(models.Identity.subject == payload["sub"])
        .one_or_none()
    )
    app.logger.info("user: {}".format(user))
    return user


if __name__ == "__main__":
    app.run(port=3000)
