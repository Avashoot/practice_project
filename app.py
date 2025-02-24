import os
import secrets
import redis

from flask import Flask, jsonify
from flask_smorest import Api # type: ignore

from db import db
from flask_jwt_extended import JWTManager
from blocklist import BLOCKLIST
from flask_migrate import Migrate # type: ignore


from resources.Item import blp as ItemBlueprint
from resources.store import blp as StoreBlueprint
from resources.tag import blp as TagBlueprint
from resources.user import blp as UserBlueprint


def create_app(db_url= None):
    app = Flask(__name__)

    # for registering these created Blueprint with the api
    # Write a configuration options for the API

    # this is for if their any exception is occur in the extension of class
    # then propagate it in the main app
    app.config["PROPAGATE_EXCEPTION"] = True

    # flask_smorest configurations
    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    # here OPENAPI_VERSION it is a standard default
    app.config["OPENAPI_VERSION"] = "3.0.3"

    # this is for url prefix -> url start with
    app.config["OPENAPI_URL_PREFIX"] = "/"

    # This is for UI of the website
    app.config["OPENAPI_SWAGGER_UI_PATH"] ="/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

    # this for using sqlalchemy in flask app
    # if the database_url is available it is use that URL else it uses the "sqlite:///data.db"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL", "sqlite:///data.db")

    # this for sqlalchemy track modifications, which basically we don't need it slows down the sqlalchemy
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # initializes the flask sqlalchemy extension giving it our flask app
    db.init_app(app)

    # migrate the data base using flask_migrate
    # this line must be added after the db.init_app(app)
    # this line get added long after we are using the SQLAlchemy 
    # since we are using the flask migrate to create our database tables 
    # we no longer need to SQLAlchemy to do it 
    # So, we now removing the lines that execute the db.create_all()
    migrate = Migrate(app, db)

    # this is for the connect the flask smorest extension with Flask app
    api = Api(app)

    # basically this is check whether the user is created jwt somewhere else
    # we can use secrets in python to generate the key
    app.config["JWT_SECRET_KEY"] = "234429126190786516797306514623429069327" 
    jwt = JWTManager(app)

    # this call back function checks the payloads token is present in the blocklist or not
    # if this comes out to be true then the user get logged out 
    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {"description": "The token has been revoked", "error": "token_revoked"}
            ),
            401,
        )

    # adding the additional information to jwt after getting an access
    # ex. check whether the user is admin or not
    @jwt.additional_claims_loader
    def add_claims_to_jwt(identity):
        # look on to the database and see whether the user is admin
        if identity == "1" :
            return {"is_admin" : True}
        return {"is_admin" : False}

    # handling the error message given by jwt
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({
                "message" : "The token has expired.", "error": "token_expired" 
            }), 401
        )
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return(
            jsonify({
                "message" : "Signature verification failed.", "error": "invalid_token" 
            }), 401
        )
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return(
            jsonify({
                "description" : "Request does not contain an access token.", "error": "authorization_required" 
            }), 401
        )
    
    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return(
            jsonify({
                "description" : "The token is not fresh.", "error": "fresh_token_required" 
            }), 401
        )

    # this is the function that executed before our first request get processed
    # with app.app_context():
    #     db.create_all() # if the tables are already exist it don't create it

    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(TagBlueprint)
    api.register_blueprint(UserBlueprint)

    return app
