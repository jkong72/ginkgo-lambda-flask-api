# id
# 1 = 식당
# 2 = 교통
# 3 = OTT

# 키워드 리스트
keyword_list = [['순대국', '치킨', '피자', '파파존스'], ['지하철', '버스', '기차'], ['넷플릭스', '왓챠']]

# 새로 카테고리를 지정할 통장 인자
print_content = '무봉리순대국'

if print_content in DB: # 식별테이블에 이미 등록되어 있는 통장인자
    pass
else : # 식별테이블에 등록되어있지 않은 통장인자
    # 키워드가 포함되어 있는지 확인
    for id in keyword_list:
        for keyword in keyword_list[id]:
            if keyword in print_content:
                type_id = id+1