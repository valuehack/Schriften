import mysql.connector
import os

base_dir = os.path.dirname(os.path.abspath(__file__))

class Connector:

    config = {}

    def __init__(self):
        with open(os.path.join(base_dir, 'database.key'), 'r') as f:
            lines = f.readlines()
            self.config = {
                'user': lines[0].strip(),
                'password': lines[1].strip(),
                'host': lines[2].strip(),
                'database': lines[3].strip(),
                # 'raise_on_warnings': lines[4].strip(),
                # 'use_unicode': lines[5].strip(),
                # 'collation': lines[6].strip()
            }


    def query(self, query):
        try:
            cnx = mysql.connector.connect(**self.config)
        except mysql.connector.Error as err:
            print(err)
            return False
        else:
            cursor = cnx.cursor(dictionary=True)
            cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
            cnx.close()
            return result

    def commit(self, query):
        try:
            cnx = mysql.connector.connect(**self.config)
        except mysql.connector.Error as err:
                print(err)
        else:
            cursor = cnx.cursor(buffered=True)
            cursor.execute(query)
            cnx.commit()
            cursor.close()
            cnx.close()
