class Config :
    JWT_SECRET_KEY = 'yh@1234'
    # code 뒤 0은 더미 데이터
    Token_GET_URL = 'https://testapi.openbanking.or.kr/oauth/2.0/token?code=0&client_secret=980fb060-8387-4dd1-8f3a-989d3083fe4e&redirect_uri=http://localhost:5000/&grant_type=authorization_code'