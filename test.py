from utils_fold.url_request import auto_increment_num


num = 0
for i in range(10):
    num = auto_increment_num(num)
    print(num)

