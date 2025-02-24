from flask.views import MethodView
from flask_smorest import Blueprint, abort # type: ignore
from sqlalchemy.exc import SQLAlchemyError
from models import ItemModel
from db import db
from schemas import ItemSchema, UpdateItemSchema
from flask_jwt_extended import jwt_required, get_jwt
# This is file is the same as the store.py But 
# In this file their is just operations on the Items in the store 

blp = Blueprint("Items", __name__, description="Operations on item")

@blp.route("/item/<int:item_id>")
class Item(MethodView):

    @jwt_required()
    @blp.response(200, ItemSchema)
    def get(self, item_id):
        item = ItemModel.query.get_or_404(item_id)
        return item

    @jwt_required()
    def delete(self, item_id):
        jwt = get_jwt()
        if not jwt.get("is_admin"):
            abort(401, message="Admin privilege required.")
        item = ItemModel.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return {"Message": "item deleted"}
    
    @jwt_required()
    @blp.arguments(UpdateItemSchema)
    @blp.response(200, ItemSchema)
    def put(self, new_item_data, item_id):
        # we need to put new_item_data just after the self
        #  here we running idempotent request because if user click multiple time then also its execute only once
        item = ItemModel.query.get(item_id)
        if item:
            item.item_name = new_item_data["item_name"]
            item.item_price = new_item_data["item_price"]
        else:
            item = ItemModel(item_id= item_id,**new_item_data)
        db.session.add(item)
        db.session.commit()
        
        return item


@blp.route("/item")
class ItemList(MethodView):
    #here we are using marshmallow for validation and response
    # so while returning before we are using {"items" : list(items.values())}
    # But now ItemSchema(many=True) at the beginning 
    # while returning already it convert it into lis so, just return 
    @jwt_required()
    @blp.response(200,ItemSchema(many=True))
    def get(self):
        return ItemModel.query.all() # will now return a list of items not a object with list of items

    @jwt_required()
    @blp.arguments(ItemSchema)
    @blp.response(201, ItemSchema)
    def post(self, item_data):
        # we are now using the marshmallow schemas for validation purposes
        # so, we don't need tp use request.get_json() shown below
        # item_data = request.get_json()
        # this for checking the JSON payload is correct or not
        item = ItemModel(**item_data)

        try:
            # you can add multiple sessions but you just need to commit only once
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occur while inserting the item")
        return item