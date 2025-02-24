from db import db

class TagModel(db.Model): #type: ignore
    __tablename__ = "tags"

    tag_id = db.Column(db.Integer, primary_key = True)
    tag_name = db.Column(db.String(80), unique = True, nullable = False)
    store_id = db.Column(db.String, db.ForeignKey("stores.store_id"), nullable = False)

    store= db.relationship("StoreModel", back_populates = "tags")
    # tags get populates with items only when secondary table matches the data "items_tags"
    # it back_populates going through secondary table
    items = db.relationship("ItemModel", back_populates = "tags", secondary = "items_tags") 