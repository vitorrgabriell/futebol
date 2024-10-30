from flask import Flask, jsonify
from config import create_app, get_db_connection
from collections import OrderedDict

app = Flask(__name__)

@app.route('/clubes', methods=['GET'])
def get_clubes():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute('SELECT * FROM clube')
    clubes = cursor.fetchall()

    clubes_list = []
    for clube in clubes:
        clubes_list.append(OrderedDict({
            'clube_id': clube['clube_id'],
            'nome': clube['nome'],
            'localidade': clube['localidade'],
            'data_fundacao': clube['data_fundacao'].strftime('%Y-%m-%d')
        }))

    cursor.close()
    conn.close()

    return jsonify(clubes_list)

@app.route('/jogadores', methods=['GET'])
def get_jogadores():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute('SELECT * FROM jogador')
    jogadores = cursor.fetchall()
    
    cursor.close()
    conn.close()

    return jsonify(jogadores)

if __name__ == '__main__':
    app.run(debug=True)
