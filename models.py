import datetime
from app import secret, algo
from marshmallow import Schema, fields
import hashlib
import base64
import jwt, calendar
from setup_db import db


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class DirectorSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class GenreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    password = db.Column(db.String)
    role = db.Column(db.String)

    def get_hash(self):
        return hashlib.md5(self.password.encode('utf-8')).hexdigest()

    def generate_password_hash(self):
        return base64.b64encode(self.get_hash()).decode('utf-8')

    def compare_password(self, password_hash):
        return self.generate_password_hash(self.password) == password_hash

    def generate_token(self, password_hash, is_refresh=True):
        if self.username is None:
            return None

        if not is_refresh:
            if not self.compare_password(password_user=self.password, password_hash=password_hash):
                return None

        data = {
            "username": self.username,
            "password": self.password
        }

        min15 = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
        data["exp"] = calendar.timegm(min15.timetuple())
        access_token = jwt.encode(data, secret, algorithm=algo)

        min_day = datetime.datetime.utcnow() + datetime.timedelta(days=130)
        data["exp"] = calendar.timegm(min_day.timetuple())
        refresh_token = jwt.encode(data, secret, algorithm=algo)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }

    def approve_token(self, token):
        data = jwt.decode(token, key=secret, algorithms=algo)
        username = data.get("username")
        password = data.get("password")

        return self.generate_token(username=username, password=password, password_hash=None, is_refresh=True)


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str()
    password = fields.Str()
    role = fields.Str()