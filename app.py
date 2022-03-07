from flask import Flask, jsonify, make_response

# JWT 사용을 위한 SECRET_KEY 정보가 들어있는 파일 임포트
from config import Config
from flask.json import jsonify
from http import HTTPStatus
from flask_restful import Api
from flask_jwt_extended import JWTManager



app = Flask(__name__)

# 환경변수 셋팅
app.config.from_object(Config)

# JWT 토큰 만들기
jwt = JWTManager(app)


# @jwt.token_in_blocklist_loader
# def check_if_token_is_revoked(jwt_header, jwt_payload) :
#     jti = jwt_payload['jti']
#     return jti in jwt_blacklist

api = Api(app)

# 경로와 리소스를 연결한다.
api.add_resource( UserRegisterResource, '/user/register')
api.add_resource( UserLoginResource, '/user/login')
api.add_resource( UserLogoutResource, '/user/logout')


if __name__ == '__main__' :
    app.run()
