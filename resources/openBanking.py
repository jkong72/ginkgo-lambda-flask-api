from flask import *
from http import HTTPStatus
from flask_restful import Resource
from numpy import dtype
import requests
from config import *


#### 고정값
# client_id
# redirect_uri
# scope
# state
# auth_type

#### code 값을 가져온다
# response_type

class testResource(Resource) :
    def get(self) :
        get_code = request.args.get('code')
        info = requests.post(Config.Token_GET_URL.replace('code=0','code='+get_code))

        


    