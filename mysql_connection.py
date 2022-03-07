import mysql.connector

def get_connection() :
    connection = mysql.connector.connect(host = 'yh-db.cvoukkfbturw.ap-northeast-2.rds.amazonaws.com', 
            database = 'ginkgo_db', 
            user = 'ginkgo_user2',
            password = '5214'
    )
    return connection