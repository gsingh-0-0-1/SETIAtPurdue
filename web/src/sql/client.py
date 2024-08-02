import mysql.connector as mysql
import os

from src.helpers import random_string_token

class MySQLClient:
    def __init__(self):
        self.cnx = mysql.connect(
            user='root',
            password=os.environ.get("MYSQL_ROOT_PASSWORD"),
            database='mysql',
            host='cseti-mysql',
            port=3306
        )

        TIMEOUT = 7 * 24 * 60 * 60

        cursor = self.cnx.cursor()

        cursor.execute(f'SET GLOBAL connect_timeout={TIMEOUT}')
        cursor.execute(f'SET GLOBAL interactive_timeout={TIMEOUT}')
        cursor.execute(f'SET GLOBAL wait_timeout={TIMEOUT}')

        cursor.execute("""CREATE TABLE IF NOT EXISTS userpass(
            user VARCHAR(255) PRIMARY KEY, 
            pwhash VARCHAR(255),
            conf VARCHAR(1),
            conftoken VARCHAR(255),
            create_dt DATETIME,
            conf_dt DATETIME
            )
        """)

        cursor.execute("""CREATE TABLE IF NOT EXISTS userinfo(
            user VARCHAR(255) PRIMARY KEY,
            fullname VARCHAR(255),
            email VARCHAR(255),
            affil VARCHAR(255)
            )
        """)

        cursor.execute("""CREATE TABLE IF NOT EXISTS completed_trainings(
            user VARCHAR(255),
            training_id INT,
            dt DATETIME
            )
        """)

        cursor.execute("""CREATE TABLE IF NOT EXISTS trainings(
            id INT PRIMARY KEY,
            description VARCHAR(255)
            )
        """)

        cursor.execute("""CREATE TABLE IF NOT EXISTS datareviews(
            filename VARCHAR(255),
            user VARCHAR(255),
            rating_class INT,
            dt DATETIME
            )
        """)
        cursor.close()

    def get_user_pwhash(self, user):
        cursor = self.cnx.cursor()
        cursor.execute("""
            SELECT pwhash
            FROM userpass
            WHERE
                user=%(user)s
                AND
                conf='Y'
        """, {
            'user': user
        })
        result = cursor.fetchall()
        cursor.close()
        if len(result) == 0:
            return None
        pwhash = result[0][0]
        return pwhash

    def get_user_info(self, user):
        cursor = self.cnx.cursor()
        cursor.execute("""
            SELECT user, fullname, email, affil
            FROM userinfo
            WHERE user=%(user)s
        """, {
            'user': user
        })
        result = cursor.fetchall()[0]
        cursor.close()
        return {
            "user": user,
            "fullname" : result[1],
            "email": result[2],
            "affil": result[3]
        }

    def create_new_user(self, user, pwhash, fullname, email, affil, conftoken):
        cursor = self.cnx.cursor()
        cursor.execute("""
            INSERT INTO userpass
            VALUES
            (
                %(user)s,
                %(pwhash)s,
                'N',
                %(conftoken)s
            )
        """, {
            'user': user,
            'pwhash': pwhash,
            'conftoken': conftoken
        })
        cursor.execute("""
            INSERT INTO userinfo
            VALUES
            (
                %(user)s,
                %(fullname)s,
                %(email)s,
                %(affil)s
            )
        """, {
            'user': user,
            'fullname': fullname,
            'email': email,
            'affil': affil
        })
        self.cnx.commit()
        cursor.close()

    def check_user_exists(self, user):
        cursor = self.cnx.cursor()
        cursor.execute("""
            SELECT COUNT(1)
            FROM userpass
            WHERE 
                user=%(user)s
        """, {
            'user': user
        })
        result = cursor.fetchall()
        cursor.close()
        if result[0][0] == 0:
            return False
        return True

    def get_user_from_conftoken(self, conftoken):
        cursor = self.cnx.cursor()
        cursor.execute("""
            SELECT user
            FROM userpass
            WHERE
                conftoken=%(conftoken)s
        """, {
            'conftoken': conftoken
        })
        result = cursor.fetchall()
        cursor.close()
        if len(result) == 0:
            return None
        return result[0][0]

    def confirm_user(self, user):
        cursor = self.cnx.cursor()
        cursor.execute("""
            UPDATE userpass
            SET conf='Y'
            WHERE user=%(user)s
        """, {
            'user': user
        })
        self.cnx.commit()
        cursor.close()
