import os
import psycopg2.extras
import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv

load_dotenv()


class GetDB:
    def __init__(self, min_con=2, max_con=25, con_string=''):

        self.con_string = con_string
        self.min_con = min_con
        self.max_con = max_con

    def get_db_connection(self):

        try:
            postgreSQL_pool = psycopg2.pool.SimpleConnectionPool(self.min_con, self.max_con, self.con_string)

            # Use getconn() to Get Connection from connection pool
            return postgreSQL_pool

        except (Exception, psycopg2.DatabaseError) as error:
            print("Error while connecting to PostgreSQL", error)


# get_db = GetDB(con_string=os.getenv('DB_URL')).get_db_connection()
