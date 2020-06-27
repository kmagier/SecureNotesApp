import os

DB_TYPE = 'postgresql'
DB_CONNECTOR = 'psycopg2'
USERNAME = os.environ.get('POSTGRES_USER')
PASSWORD = os.environ.get('POSTGRES_PASSWORD')
PORT = '5432'
HOST = 'psql' + ':' + PORT
DB_NAME = os.environ.get('POSTGRES_DB')

DB_URI = DB_TYPE + "+" + DB_CONNECTOR +'://' + USERNAME +':' + PASSWORD + "@" + HOST + '/' + DB_NAME