import os

DB_TYPE = 'postgresql'
DB_CONNECTOR = 'psycopg2'
DB_USERNAME = os.environ.get('POSTGRES_USER')
DB_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
PORT = '5432'
HOST = 'psql' + ':' + PORT
DB_NAME = os.environ.get('POSTGRES_DB')
DB_URI = DB_TYPE + "+" + DB_CONNECTOR +'://' + DB_USERNAME +':' + DB_PASSWORD + "@" + HOST + '/' + DB_NAME

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'some-random-secret-key'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or DB_URI   
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') or True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

