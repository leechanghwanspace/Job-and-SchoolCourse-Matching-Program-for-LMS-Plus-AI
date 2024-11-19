# db_connection.py

import mysql.connector

def connect_to_db():
    # MySQL에 연결
    connection = mysql.connector.connect(
        host='127.0.0.1',  # MySQL 서버 호스트 주소
        user='root',       # MySQL 사용자명
        password='qwerqwer', # MySQL 비밀번호
        database='lms'       # 연결할 데이터베이스 이름
    )
    return connection

# 바로 사용할 수 있도록 객체 생성
db_connection = connect_to_db()