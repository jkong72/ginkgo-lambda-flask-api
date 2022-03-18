# url의 파라미터를 엮어서 url을 완성하는 함수
def url_binder (url_list):
    url = ''
    for word in url_list:
        url = url+word
        if url_list.index(word) != 0: # 첫번째가 아니라면 &로 이어줌
            url = url+'&'

    url = url.strip('&') # 맨 마지막에 붙은 & 제거
    return url