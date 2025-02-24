from db import db


class ItemModel(db.Model): #type: ignore
    __tablename__ = "items"

    item_id = db.Column(db.Integer, primary_key= True)
    item_name = db.Column(db.String(80), unique=False, nullable=False)
    item_description = db.Column(db.String)
    item_price= db.Column(db.Float(precision=2), unique=False, nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey("stores.store_id"), unique=False, nullable= False)
    # grab me a store object with th above store_id
    store = db.relationship("StoreModel" , back_populates="items")

    tags = db.relationship("TagModel", back_populates = "items", secondary= "items_tags")