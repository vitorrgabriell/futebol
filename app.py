from flask import Flask, jsonify, request
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

@app.route('/campeonatos', methods=['GET'])
def get_campeonatos():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('SELECT * FROM campeonato')
    campeonatos = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(campeonatos)

@app.route('/jogos', methods=['GET'])
def get_jogo():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('SELECT * FROM jogo')
    jogos = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(jogos)

@app.route('/usuarios', methods=['GET'])
def get_usuario():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('SELECT * FROM usuario')
    usuarios = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(usuarios)

@app.route('/estatisticas', methods=['GET'])
def get_estatisticas():
    nome_clube = request.args.get('clube')
    nome_campeonato = request.args.get('campeonato')
    nome_jogador = request.args.get('jogador')

    if not nome_clube and not nome_jogador and not nome_campeonato:
        return jsonify({"error": "É necessário fornecer pelo menos o nome de um clube, jogador ou campeonato para visualizar as estatísticas."}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = '''
    SELECT e.*, j.data, c.nome AS nome_clube, cmp.nome AS nome_campeonato, jog.nome AS nome_jogador
    FROM estatistica_jogo e
    JOIN jogo j ON e.jogo_id = j.jogo_id
    JOIN clube c ON (j.clube_casa_id = c.clube_id OR j.clube_visitante_id = c.clube_id)
    JOIN campeonato cmp ON j.campeonato_id = cmp.campeonato_id
    LEFT JOIN jogador jog ON e.jogador_id = jog.jogador_id
    WHERE 1=1
    '''
    
    params = []

    if nome_clube:
        query += " AND c.nome = %s"
        params.append(nome_clube)

    if nome_campeonato:
        query += " AND cmp.nome = %s"
        params.append(nome_campeonato)

    if nome_jogador:
        query += " AND jog.nome = %s"
        params.append(nome_jogador)

    cursor.execute(query, tuple(params))
    estatisticas = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(estatisticas)

if __name__ == '__main__':
    app.run(debug=True)
