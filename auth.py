from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_restful import Resource, Api
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)




app_auth = Flask(__name__)
api = Api(app_auth)
app_auth.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost:3306/Kampus'
ma = Marshmallow(app_auth)
db = SQLAlchemy(app_auth)
app_auth.config['JWT_SECRET_KEY'] = 'super-secret'
jwt = JWTManager(app_auth)




class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))

    def __init__(self, username, password):
        self.username = username
        self.password = password

    @staticmethod
    def get_all_users():
        return User.query.all()


class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'username', 'password')


user_schema = UserSchema()
users_schema = UserSchema(many=True)

class apps(Resource):
    @app_auth.route('/user/', methods=['POST'])
    @jwt_required
    def create_user():
        username = request.json['username']
        password = request.json['password']

        new_user = User(username, password)

        db.session.add(new_user)
        db.session.commit()

        return user_schema.jsonify(new_user)


    @app_auth.route('/user/', methods=['GET'])
    @jwt_required
    def get_users():
        all_users = User.get_all_users()
        result = users_schema.dump(all_users)
        return jsonify(result)

    @app_auth.route('/user/<id>', methods=['GET'])
    @jwt_required
    def get_user(id):
        user = User.query.get(id)
        return user_schema.jsonify(user)

    @app_auth.route('/user/<id>', methods=['PUT'])
    @jwt_required
    def update_user(id):
        user = User.query.get(id)

        username = request.json['username']
        password = request.json['password']

        user.username = username
        user.password = password


        db.session.commit()

        return user_schema.jsonify(user)

    @app_auth.route('/user/<id>', methods=['DELETE'])
    @jwt_required
    def delete_product(id):
        user = User.query.get(id)
        db.session.delete(user)
        db.session.commit()

        return user_schema.jsonify(user)



    @app_auth.route('/login', methods=['POST'])
    def login():
        if not request.is_json:
            return jsonify({"msg": "Missing JSON in request"}), 400

        username = request.json.get('username', None)
        password = request.json.get('password', None)

        login_user = User.query.filter_by(username=username).first()
        print(login_user.username + " " + username)
        print(login_user.password + " " + password)

        if not username:
            return jsonify({"msg": "Missing username parameter"}), 400
        if not password:
            return jsonify({"msg": "Missing password parameter"}), 400

        if username != login_user.username or password != login_user.password:  # 1 or 0 = 1 1 and 1 = 1
            return jsonify({"msg": "Bad username or password"}), 401

        # Identity can be any data that is json serializable
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200

api.add_resource(apps, '/login',  endpoint='apps_ep')


if __name__ == '__main__':
  app_auth.run(debug=True)
