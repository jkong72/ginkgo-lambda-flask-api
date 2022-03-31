from flask_restful import Resource
from flask import request
from http import HTTPStatus
from mysql.connector.errors import Error
from flask_jwt_extended import jwt_required, get_jwt_identity

from mysql_connection import get_connection

rep_ok = 0
rep_err = 1
def get_classification_list(connection, user_id):
    print("Start request get_classification_list data")
    

    
    return { 'error' : rep_ok,'classification_list' : classification_list, "keyword_list" : keyword_list }, HTTPStatus.OK