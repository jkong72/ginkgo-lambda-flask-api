from flask import Flask, jsonify, make_response,request
from config import Config
from flask.json import jsonify
from http import HTTPStatus
from flask_restful import Api
from flask_jwt_extended import JWTManager
from resources.openBanking import OpenBankingResource

from resources.user_login import UserLoginResource, UserLogoutResource, UserRegisterResource 
from resources.user_login import jwt_blacklist
########################################
# 실제 개발 부분 ########################
########################################
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

# 경로와 리소스를 연결한다.
api.add_resource( UserRegisterResource, '/user/register') # 유저 회원가입
api.add_resource( UserLoginResource, '/user/login2') # 유저 로그인
api.add_resource( UserLogoutResource, '/user/logout') # 유저 로그아웃
api.add_resource( OpenBankingResource, '/user/openbanking')

if __name__ == '__main__' :
    app.run()

