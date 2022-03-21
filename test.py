from flask import *
from http import HTTPStatus
from flask_restful import Resource
from numpy import dtype
import requests
from config import *
from flask.json import jsonify
from dateutil.relativedelta import *
import datetime as dt

def test():
    b = dt.date(2020, 7, 25)
    # print(b)
    # b= b.strftime('%Y%m%d')
    # print(b)

    
    a = b+relativedelta(days=50)
    print(a)

test()