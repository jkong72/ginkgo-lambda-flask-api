# 불러오기
from mysql_connection import get_connection
from mysql.connector.errors import Error
import pandas as pd
import numpy as np
 
def getList(email):    
        
    cnt = get_connection()
    cursor = cnt.cursor()

    query = '''select email, password from user where email = %s; '''
    cursor = cnt.cursor(dictionary = True)
    
    record_list = cursor.fetchall()
    print(record_list)
    print(record_list[2][2])
    
    # price = []
    list = []
    for row in record_list:
        # price.append(row[2])
        list.append(row)
    
    cnt.close()
    return list
 
