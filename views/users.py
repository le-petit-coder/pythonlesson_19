from flask_restx import Resource, Namespace
from flask import request
from app import admin_required, auth_required
from models import User, UserSchema
from setup_db import db

users_ns = Namespace('users')


@users_ns.route('/')
class UsersView(Resource):
    def get(self):
        rs = db.session.query(User).all()
        res = UserSchema(many=True).dump(rs)
        return res, 200

    def post(self):
        req_json = request.json
        if not req_json.get("username") and not req_json.get("password") and not req_json.get("role"):
            return "data not entered", 401

        ent = User(**req_json)
        db.session.add(ent)
        db.session.commit()
        return "", 201, {"location": f"/users/{ent.id}"}


@users_ns.route('/<int:rid>')
class UserView(Resource):
    def get(self, rid):
        r = db.session.query(User).get(rid)
        sm_d = UserSchema().dump(r)
        return sm_d, 200

    def put(self, did):
        user = db.session.query(User).get(did)
        req_json = request.json
        user.name = req_json.get("username")
        db.session.add(user)
        db.session.commit()
        return "", 204

    def delete(self, did):
        user = db.session.query(User).get(did)

        db.session.delete(user)
        db.session.commit()
        return "", 204