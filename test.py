from flask import *
from http import HTTPStatus
from flask_restful import Resource
from numpy import dtype
import requests
from config import *
from flask.json import jsonify


def test():
    get_code = '4dlNRkdo1stR6PJm1Tt3D2ox2kNgQL'
    params = {"code":get_code, "client_id": "fde4d72d-e26b-492c-9d66-d7ef9014cd59", "client_secret": "980fb060-8387-4dd1-8f3a-989d3083fe4e", "redirect_uri":"http://localhost:5000/","grant_type": "authorization_code"}
    info = requests.post(Config.Token_GET_URL, params=params)

    info = info.text
    print(info)


test()