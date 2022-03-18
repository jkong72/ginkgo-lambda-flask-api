from flask_restful import Resource
from flask import request
from http import HTTPStatus
from mysql.connector.errors import Error
from flask_jwt_extended import jwt_required, get_jwt_identity


request