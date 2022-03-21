from flask import Flask, jsonify, make_response
from flask.json import jsonify
from flask_restful import Api
from http import HTTPStatus

from flask_jwt_extended import JWTManager
from config import Config

from resources.budget.budget import budgetResource
from resources.budget.budget_edit import budgetEditResource


########################################
# 실제 개발 부분 ########################
########################################
app = Flask(__name__)

# 환경변수 셋팅
app.config.from_object(Config)

# JWT 토큰 만들기
jwt = JWTManager(app)

# api 구성
api = Api(app)

# 경로와 리소스를 연결한다.
api.add_resource(budgetResource, '/budget')                         # 예산 가져오기 및 추가
api.add_resource(budgetEditResource,  '/budget/<int:budget_id>')    # 예산 수정 및 삭제

api.add_resource()

if __name__ == '__main__' :
    app.run()
