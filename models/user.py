from db import db

class UserModel(db.Model): #type:ignore
    __tablename__= "UserData"

    user_id = db.Column(db.Integer, primary_key= True)
    username = db.Column(db.String(100), unique = True, nullable = False)
    password = db.Column(db.String(100),  nullable = False)