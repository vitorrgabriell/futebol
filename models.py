from config import db

class Clube(db.Model):
    __tablename__ = 'clube'
    clube_id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    localidade = db.Column(db.String(100))
    data_fundacao = db.Column(db.Date)

class Jogador(db.Model):
    __tablename__ = 'jogador'
    jogador_id = db.Column(db.Integer, primary_key=True)
    clube_id = db.Column(db.Integer, db.ForeignKey('clube.clube_id'), nullable=True)
    nome = db.Column(db.String(100), nullable=False)
    data_nascimento = db.Column(db.Date)
    posicao = db.Column(db.String(50))
    altura = db.Column(db.Float)
    peso = db.Column(db.Float)
    cidade_natal = db.Column(db.String(100))

    # Relacionamento com o clube
    clube = db.relationship('Clube', backref='jogadores')

class Usuario(db.Model):
    __tablename__ = 'usuario'
    usuario_id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    tipo = db.Column(db.Enum('representante', 'tecnico_agente'), nullable=False)
    clube_id = db.Column(db.Integer, db.ForeignKey('clube.clube_id'), nullable=True)

    # Relacionamento com o clube
    clube = db.relationship('Clube', backref='usuarios')

class Campeonato(db.Model):
    __tablename__ = 'campeonato'
    campeonato_id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    ano = db.Column(db.Integer, nullable=False)
    tipo = db.Column(db.String(50))

class Jogo(db.Model):
    __tablename__ = 'jogo'
    jogo_id = db.Column(db.Integer, primary_key=True)
    campeonato_id = db.Column(db.Integer, db.ForeignKey('campeonato.campeonato_id'), nullable=True)
    clube_casa_id = db.Column(db.Integer, db.ForeignKey('clube.clube_id'), nullable=True)
    clube_visitante_id = db.Column(db.Integer, db.ForeignKey('clube.clube_id'), nullable=True)
    data = db.Column(db.Date, nullable=False)
    local = db.Column(db.String(100))

    # Relacionamentos
    campeonato = db.relationship('Campeonato', backref='jogos')
    clube_casa = db.relationship('Clube', foreign_keys=[clube_casa_id], backref='jogos_casa')
    clube_visitante = db.relationship('Clube', foreign_keys=[clube_visitante_id], backref='jogos_visitante')

class EstatisticaJogo(db.Model):
    __tablename__ = 'estatistica_jogo'
    estatistica_id = db.Column(db.Integer, primary_key=True)
    jogo_id = db.Column(db.Integer, db.ForeignKey('jogo.jogo_id'), nullable=False)
    jogador_id = db.Column(db.Integer, db.ForeignKey('jogador.jogador_id'), nullable=True)
    tipo = db.Column(db.Enum('gol', 'cartao_amarelo', 'cartao_vermelho', 'falta', 'escanteio', 'impedimento', 'substituicao'), nullable=False)
    valor = db.Column(db.Integer, default=1)
    minuto = db.Column(db.Integer)

    # Relacionamentos
    jogo = db.relationship('Jogo', backref='estatisticas')
    jogador = db.relationship('Jogador', backref='estatisticas')
