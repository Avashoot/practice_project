import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort # type: ignore
from flask_jwt_extended import jwt_required

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from db import db
from models import StoreModel

from schemas import StoreSchema

# The Blueprint in flask_smorest used to divide API into multiple segments
# Here instance of Blueprint class thats  come with the 3 attributes
# .............<name_tag>, gating_name, desc of the instance
blp = Blueprint("stores", __name__, description="Operations on store")

# blp.route used for the routing with the different API's just like the 
# app.get(), .post(), .put(), .delete()
# instead of using same routing again and again we create teh class of the same 
#  routing  methods, here comes the use of BluePrint flask smorest
@blp.route("/store/<int:store_id>")
class Store(MethodView):
    # The above MethodView is a class its get Inherited By the classes  for creating
    # the classes and their routing or REST methods in flask
    # the below get() method act as app.get("url/<id>")
    # this get() method is for the information about that store
    @jwt_required()
    @blp.response(200, StoreSchema)
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store

    #  this delete() delete the store data
    @jwt_required()
    def delete(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        db.session.delete(store)
        db.session.commit()
        return {"Message" : "Store deleted"}


@blp.route("/store")
class StoreList(MethodView):
    # this is for the get the data of the all the stores
    @jwt_required()
    @blp.response(200, StoreSchema(many=True))
    def get(self):
        return StoreModel.query.all() # return list because StoreSchema(many=True)

    # this is for the add the new store in the database
    @jwt_required()
    @blp.arguments(StoreSchema)
    @blp.response(201, StoreSchema)
    def post(self, store_data):
        store = StoreModel(** store_data)

        try:
            db.session.add(store)
            db.session.commit()
        except IntegrityError:
            abort(
                400, message="Store with that name already exists."
            )
        except SQLAlchemyError:
            abort(
                500, message="An error occur while creating the store"
            )
        
        return store
