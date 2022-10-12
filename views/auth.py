from flask_restx import Resource, Namespace
from flask import request
from models import User

auth_ns = Namespace('users')


@auth_ns.route('/')
class AuthView(Resource):
    def post(self):
        req_json = request.json
        username = req_json.get("username")
        password = req_json.get("password")

        if not username and not password:
            return "No data", 401

        return User.generate_token(
            username=username,
            password=password,
            password_hash=User.get_hash()
        )

    def put(self):
        req_json = request.json

        if not req_json.get("refresh_token"):
            return "refresh_token not entered", 401

        return User.approve_token(
            token=req_json.get("refresh_token")
        ), 200
