from flask import Flask
import mysql.connector

def create_app():
    app = Flask(__name__)

    # Configurações do banco de dados
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = ''  # Deixe vazio se não tiver senha
    app.config['MYSQL_DB'] = 'futebol'

    return app

# Função para conectar ao banco de dados
def get_db_connection():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',  # Coloque a senha se houver
        database='futebol'
    )
    return conn
