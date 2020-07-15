from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_restful import Resource, Api
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)


app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost:3306/Kampus'
ma = Marshmallow(app)
db = SQLAlchemy(app)
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!
jwt = JWTManager(app)


class Mahasiswa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nim = db.Column(db.CHAR(10), unique=True)
    nama = db.Column(db.CHAR(100))
    alamat= db.Column(db.String(100))

    def __init__(self, nim, nama, alamat):
        self.nim = nim
        self.nama = nama
        self.alamat = alamat

    @staticmethod
    def get_all_users():
        return Mahasiswa.query.all()


class UserSchema(ma.Schema):
    class Meta:
        fields = ('id','nim', 'nama', 'alamat')


user_schema = UserSchema()
users_schema = UserSchema(many=True)

class MahasiswaApi(Resource):
    @jwt_required
    def get(self, id=None):
      if id is not None:
        mahasiswa = Mahasiswa.query.get(id)
        return user_schema.jsonify(mahasiswa)
      else:
        all_users = Mahasiswa.get_all_users()
        result = users_schema.dump(all_users)
        return jsonify(result)

    @jwt_required
    def post(self):
        nim = request.json['nim']
        nama = request.json['nama']
        alamat = request.json['alamat']
        new_mhs = Mahasiswa(nim, nama, alamat)

        db.session.add(new_mhs)
        db.session.commit()

        return user_schema.jsonify(new_mhs)

    @jwt_required
    def put(self, id):
        mahasiswa = Mahasiswa.query.get(id)
        nim = request.json['nim']
        nama = request.json['nama']
        alamat = request.json['alamat']


        mahasiswa.nim = nim
        mahasiswa.nama = nama
        mahasiswa.alamat = alamat

        db.session.commit()

        return user_schema.jsonify(mahasiswa)
    @jwt_required
    def delete(self, id):
        mahasiswa = Mahasiswa.query.get(id)
        db.session.delete(mahasiswa)
        db.session.commit()

        return user_schema.jsonify(mahasiswa)


api.add_resource(MahasiswaApi, '/mahasiswa/', '/mahasiswa/<int:id>/', endpoint='mahasiswa_ep')




if __name__ == '__main__':
  app.run(debug=True)
