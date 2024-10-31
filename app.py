from flask import Flask, jsonify, request
from config import create_app, get_db_connection
from collections import OrderedDict
import datetime

app = Flask(__name__)

@app.route('/get_clubes', methods=['GET'])
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

@app.route('/get_jogadores', methods=['GET'])
def get_jogadores():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute('SELECT * FROM jogador')
    jogadores = cursor.fetchall()
    
    cursor.close()
    conn.close()

    return jsonify(jogadores)

@app.route('/get_campeonatos', methods=['GET'])
def get_campeonatos():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('SELECT * FROM campeonato')
    campeonatos = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(campeonatos)

@app.route('/get_jogos', methods=['GET'])
def get_jogo():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('SELECT * FROM jogo')
    jogos = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(jogos)

@app.route('/get_usuarios', methods=['GET'])
def get_usuario():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('SELECT * FROM usuario')
    usuarios = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(usuarios)

@app.route('/get_estatisticas', methods=['GET'])
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

@app.route('/add_clubes', methods=['POST'])
def add_clube():
    data = request.get_json()
    nome = data.get('nome')
    localidade = data.get('localidade')
    data_fundacao = data.get('data_fundacao')

    if not nome or not localidade or not data_fundacao:
        return jsonify({"error": "Nome, localidade e data de fundação são obrigatórios."}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    query = '''
    INSERT INTO clube (nome, localidade, data_fundacao)
    VALUES (%s, %s, %s)
    '''
    cursor.execute(query, (nome, localidade, data_fundacao))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"message": "Clube adicionado com sucesso!"}), 201

def clube_existe(clube_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clube WHERE clube_id = %s', (clube_id,))
    clube = cursor.fetchone()
    cursor.close()
    conn.close()
    return clube is not None

def validar_data(data_str):
    try:
        data_convertida = datetime.datetime.strptime(data_str, '%d-%m-%Y').strftime('%Y-%m-%d')
        return data_convertida
    except ValueError:
        return None

@app.route('/add_jogadores', methods=['POST'])
def add_jogador():
    data = request.get_json()
    clube_id = data.get('clube_id')
    nome = data.get('nome')
    data_nascimento = data.get('data_nascimento')
    posicao = data.get('posicao')
    altura = data.get('altura')
    peso = data.get('peso')
    cidade_natal = data.get('cidade_natal')

    if not clube_id or not nome or not data_nascimento or not posicao or not altura or not peso or not cidade_natal:
        return jsonify({"Error": "Todos os campos são obrigatórios para realizar o cadastro"}), 400

    if not clube_existe(clube_id):
        return jsonify({"Error": "Clube não encontrado"}), 400

    data_nascimento_formatada = validar_data(data_nascimento)
    if not data_nascimento_formatada:
        return jsonify({"Error": "Data de nascimento deve estar no formato DD-MM-YYYY"}), 400

    try:
        altura = float(altura)
        peso = float(peso)
    except ValueError:
        return jsonify({"Error": "Altura e peso devem ser números válidos"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    query = '''
    INSERT INTO jogador (clube_id, nome, data_nascimento, posicao, altura, peso, cidade_natal)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    '''

    cursor.execute(query, (clube_id, nome, data_nascimento_formatada, posicao, altura, peso, cidade_natal))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"message": "Jogador adicionado com sucesso!"}), 201

@app.route('/add_estatistica', methods=['POST'])
def add_estatistica():
    data = request.get_json()

    jogo_id = data.get('jogo_id')
    jogador_id = data.get('jogador_id')  # Pode ser nulo se a estatística não for de um jogador
    tipo = data.get('tipo')  # Ex: gol, cartao_amarelo, cartao_vermelho, falta
    valor = data.get('valor')  # Ex: número de gols, tipo de cartão
    minuto = data.get('minuto')

    # Validação de campos obrigatórios
    if not jogo_id or not tipo or not valor or not minuto:
        return jsonify({"Error": "Jogo, tipo de estatística, valor e minuto são obrigatórios"}), 400

    # Validação se o jogo existe
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM jogo WHERE jogo_id = %s', (jogo_id,))
    jogo = cursor.fetchone()
    if not jogo:
        return jsonify({"Error": "Jogo não encontrado"}), 400

    # Se um jogador for fornecido, validamos se ele existe
    if jogador_id:
        cursor.execute('SELECT * FROM jogador WHERE jogador_id = %s', (jogador_id,))
        jogador = cursor.fetchone()
        if not jogador:
            return jsonify({"Error": "Jogador não encontrado"}), 400

    # Inserção no banco de dados
    query = '''
    INSERT INTO estatistica_jogo (jogo_id, jogador_id, tipo, valor, minuto)
    VALUES (%s, %s, %s, %s, %s)
    '''
    cursor.execute(query, (jogo_id, jogador_id, tipo, valor, minuto))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"message": "Estatística adicionada com sucesso!"}), 201


@app.route('/add_jogo', methods=['POST'])
def add_jogo():
    data = request.get_json()

    campeonato_id = data.get('campeonato_id')
    clube_casa_id = data.get('clube_casa_id')
    clube_visitante_id = data.get('clube_visitante_id')
    data_jogo = data.get('data_jogo')
    local = data.get('local')

    if not campeonato_id or not clube_casa_id or not clube_visitante_id or not data_jogo or not local:
        return jsonify({"Error": "Todos os campos são obrigatórios para realizar o cadastro do jogo"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM campeonato WHERE campeonato_id = %s', (campeonato_id,))
    campeonato = cursor.fetchone()
    if not campeonato:
        return jsonify({"Error": "Campeonato não encontrado"}), 400

    cursor.execute('SELECT * FROM clube WHERE clube_id = %s', (clube_casa_id,))
    clube_casa = cursor.fetchone()
    if not clube_casa:
        return jsonify({"Error": "Clube mandante não encontrado"}), 400

    cursor.execute('SELECT * FROM clube WHERE clube_id = %s', (clube_visitante_id,))
    clube_visitante = cursor.fetchone()
    if not clube_visitante:
        return jsonify({"Error": "Clube visitante não encontrado"}), 400

    data_jogo_formatada = validar_data(data_jogo)
    if not data_jogo_formatada:
        return jsonify({"Error": "A data do jogo deve estar no formato DD-MM-YYYY"}), 400

    query = '''
    INSERT INTO jogo (campeonato_id, clube_casa_id, clube_visitante_id, data, local)
    VALUES (%s, %s, %s, %s, %s)
    '''
    cursor.execute(query, (campeonato_id, clube_casa_id, clube_visitante_id, data_jogo_formatada, local))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"message": "Jogo adicionado com sucesso!"}), 201

@app.route('/add_campeonato', methods=['POST'])
def add_campeonato():
    data = request.get_json()

    nome = data.get('nome')
    ano = data.get('ano')
    tipo = data.get('tipo')

    if not nome or not ano or not tipo:
        return jsonify({"Error": "Nome, ano e tipo do campeonato são obrigatórios"}), 400

    try:
        ano = int(ano)
        if ano < 1800 or ano > datetime.datetime.now().year + 1:
            return jsonify({"Error": "Ano deve ser um número válido e plausível"}), 400
    except ValueError:
        return jsonify({"Error": "Ano deve ser um número válido"}), 400

    tipos_validos = ['regional', 'nacional', 'internacional']
    if tipo.lower() not in tipos_validos:
        return jsonify({"Error": "Tipo de campeonato inválido. Valores permitidos: regional, nacional, internacional"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    query = '''
    INSERT INTO campeonato (nome, ano, tipo)
    VALUES (%s, %s, %s)
    '''
    cursor.execute(query, (nome, ano, tipo))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"message": "Campeonato adicionado com sucesso!"}), 201

if __name__ == '__main__':
    app.run(debug=True)
