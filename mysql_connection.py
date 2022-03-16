import mysql.connector

def get_connection() :
    connection = mysql.connector.connect(host = 'yh-db.cvoukkfbturw.ap-northeast-2.rds.amazonaws.com', 
            database = 'ginkgo_db', 
            user = 'ginkgo_user3',
            password = '5314'
    )
    return connection