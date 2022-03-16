# 실제 개발을 시작하면 이 파일은 삭제하고 진행하세요
# 기본적으로 수업간 진행한 것과 같은 형식으로 작성합니다.

from flask_restful import Resource
from flask import request
from http import HTTPStatus
from mysql.connector.errors import Error
from flask_jwt_extended import jwt_required, get_jwt_identity

class sample(Resource):
    def get(self):
        # DB와 연결
        # 쿼리문 작성
        # 예외처리 (에러)
        # 연결 종료
        # 결과 응답
        return {'return':'app is run'}