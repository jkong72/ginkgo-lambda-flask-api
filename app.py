from flask import Flask, jsonify, make_response, request, render_template, redirect
from flask_jwt_extended import JWTManager,jwt_required, get_jwt_identity
from config import Config

from flask_restful import Api
from resources.user_login import UserLoginResource, UserLogoutResource, UserRegisterResource , jwt_blacklist


app = Flask(__name__)

# 환경변수 셋팅
app.config.from_object(Config)

# JWT 토큰 만들기
jwt = JWTManager(app)


# jwt 토큰
@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload) :
    jti = jwt_payload['jti']
    return jti in jwt_blacklist

api = Api(app)

@app.route('/')
def route_page():
    return render_template('test.html',
    t1_x = [1, 2, 3, 4],
    t1_y = [11, 14, 16, 10],
    t2_x = [1, 2, 3, 4],
    t2_y = [14, 11, 12, 16])


print ('실행됨')



