from flask import Flask, jsonify, make_response
from flask.json import jsonify
from flask_restful import Api
from http import HTTPStatus

from flask_jwt_extended import JWTManager
from config import Config
from resources.bank_tran_id import BankTranIdResource

from resources.budget.budget import budgetResource
from resources.budget.budget_edit import budgetEditResource
from resources.trade.trade_upload import AccountInfoResource, TradeInfoResource


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

api.add_resource(AccountInfoResource, '/account')                   # DB에서 계좌 정보 조회
api.add_resource(TradeInfoResource, '/trade')                       # DB에서 거래 내역 조회

api.add_resource(BankTranIdResource, '/bank_tran_id')                       # 은행 거래 코드 입출


if __name__ == '__main__' :
    app.run()
