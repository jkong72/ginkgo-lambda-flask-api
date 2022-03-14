from flask import Flask, jsonify, make_response,request
from config import Config
from flask.json import jsonify
from http import HTTPStatus
from flask_restful import Api
from flask_jwt_extended import JWTManager

from resources.sample import sample
from resources.user_login import UserLoginResource, UserLogoutResource, UserRegisterResource # 앱 실행이 확인되면 삭제되는 라인입니다.
from resources.user_login import jwt_blacklist
########################################
# 실제 개발 부분 ########################
########################################
app = Flask(__name__)

# 환경변수 셋팅
app.config.from_object(Config)

# JWT 토큰 만들기
jwt = JWTManager(app)

# 해당부분은 소요가 발생하기 전까지는 사용하지 않음 (오픈뱅킹 인증 토큰으로 갈음함)
@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload) :
    jti = jwt_payload['jti']
    return jti in jwt_blacklist

api = Api(app)

# 경로와 리소스를 연결한다.
api.add_resource(sample, '/sample') # 앱이 작동하는지 확인하는 샘플 코드 확인되었다면 상단의 import와 현재 라인을 삭제 후 개발 진행
api.add_resource( UserRegisterResource, '/user/register')
api.add_resource( UserLoginResource, '/user/login')
api.add_resource( UserLogoutResource, '/user/logout')

if __name__ == '__main__' :
    app.run()


##################################################
# 스트림릿 개발 부분 ###############################
##################################################
# 개발 소요에 따라 이하의 부분은 별개의 파일로 분리할 수 있습니다.
# def streamlit():
#    return

# if __name__ == '__main__':
#     streamlit()