from flask.views import MethodView
from flask_smorest import abort, Blueprint #type:ignore
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.hash import pbkdf2_sha256 #type:ignore
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, get_jwt_identity, create_refresh_token
from blocklist import BLOCKLIST

from db import db
from models import UserModel
from schemas import UserSchema

blp = Blueprint("Users", "users", description = "Operations on User")


@blp.route("/register")
class UserRegister(MethodView):

    @blp.arguments(UserSchema)
    def post(self, user_data):
        # check the username is unique or not
        if  UserModel.query.filter(UserModel.username == user_data["username"]).first():
            abort(409, message="User with that username already exists.")
        
        user = UserModel(
            username = user_data["username"],
            password = pbkdf2_sha256.hash(user_data["password"])

        )

        try:
            db.session.add(user)
            db.session.commit()
        except SQLAlchemyError : 
            abort(500, message= "An error occur while registering the user.")
        
        return {"message": "User registered successfully"}, 201


@blp.route("/user/<int:user_id>")
class User(MethodView):

    @blp.response(200, UserSchema)
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        return user
    
    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        try:
            db.session.delete(user)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occur while deleting the user")
        
        return {"message": "User deleted."}, 200
    

@blp.route("/login")
class UserLogin(MethodView):

    @blp.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel.query.filter(
            UserModel.username == user_data["username"]
        ).first()

        # this is for the verifying the correct password provided by user
        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            # *! changes alert !!
            # ** when we create an access token or refresh token 
            # ** we now have to pass string as identity, not an int
            # *TODO: identity = Str(user.user_id)
            # ** we must do this for both creating the access tokens and refresh token 
            # ** only in login endpoint
            access_token = create_access_token(identity = str(user.user_id), fresh=True)
            refresh_token = create_refresh_token(identity= str(user.user_id))

            return {"access_token": access_token, "refresh_token": refresh_token}
        
        abort(401, message="Invalid credentials")

@blp.route("/logout")
class UserLogout(MethodView):

    @jwt_required()
    def post(self):
        #  we can get the access token by both the way
        # jti = get_jwt().get("jti") 
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)

        return {"message": "Successfully Logout."}
    

@blp.route("/refresh")
class TokenRefresh(MethodView):

    @jwt_required(refresh=True)
    def post(self):
        # current_user = get_jwt().get("sub") this is may be correct but below this is used most frequently
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user , fresh = False)
        return {"access_token" : new_token}


        
