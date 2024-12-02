# Importação das bibliotecas necessárias
from flask import Flask, render_template, request, redirect
import sqlite3
import re

# Criação da aplicação Flask
app = Flask(__name__)

# Função para obter a conexão com o banco de dados SQLite
def get_db_connection():
    conn = sqlite3.connect('BancoDeDados.db')
    conn.row_factory = sqlite3.Row
    return conn

# Função para criar as tabelas no banco de dados, caso não existam
def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Criação da tabela 'conta'
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conta (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_sobrenome TEXT NOT NULL,
            data_nasc TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL
        )
    ''')

    # Criação da tabela 'compra'
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS compra (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL,
            nTelefone TEXT NOT NULL,
            cep TEXT NOT NULL,
            nCasa TEXT NOT NULL,
            idproduto INTEGER NOT NULL,
            qtd INTEGER NOT NULL,
            FOREIGN KEY (idproduto) REFERENCES produto(id)
        )
    ''')

    # Criação da tabela 'produto'
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produto (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            preco REAL NOT NULL,
            tamanho TEXT NOT NULL
        )
    ''')

    cursor.execute("SELECT COUNT(*) FROM produto")
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
            INSERT INTO produto (id, nome, preco, tamanho) VALUES (?, ?, ?, ?)
        ''', [
            (1, 'Pijama Infantil Feminino de Coala', 39.90, 'Tamanho Único'),
            (2, 'Pijama Infantil Coala Azul', 60.90, 'Tamanho Único'),
            (3, 'Pijama Coala Rosa Azul Branco', 40.90, 'Tamanho Único'),
            (4, 'Pijama Infantil Feminino Manga Longa', 40.90, 'Tamanho Único'),
            (5, 'Pijama Unicórnio', 80.00, 'Tamanho Único'),
            (11, 'Pijama Azul', 39.89, 'Tamanho Único'),
            (12, 'Pijama Cinza', 89.00, 'Tamanho Único'),
            (13, 'Pijama Cetim Azul', 89.90, 'Tamanho Único'),
            (14, 'Rosa Feminino', 69.90, 'Tamanho Único'),
            (15, 'Pijama Longo Rosa Adulto Feminino Camuflado', 70.00, 'Tamanho Único'),
            (16, 'Pijama Cogumelo', 39.90, 'Tamanho Único'),
            (17, 'Pijama Vinho', 70.00, 'Tamanho Único'),
            (18, 'Pijama Adulto Masculino de Algodão Azul Bola Futebol', 29.90, 'Tamanho Único'),
            (19, 'Pijama Masculino Adulto Preto', 69.90, 'Tamanho Único'),
            (20, 'Pijama Curto Adulto Masculino com Estampa que Brilha no Escuro Monstros', 90.00, 'Tamanho Único'),
            (21, 'Pijama Adulto Masculino Capitão América em Algodão', 89.90, 'Tamanho Único'),
            (22, 'Pijama Feminino Longo Minnie Mouse', 90.90, 'Tamanho Plus-Size'),
            (23, 'Pijama Feminino Curto com Abertura Mickey', 129.90, 'Tamanho Plus-Size'),
            (24, 'Pijama Masculino Curto Americano Plus Size Azul', 59.90, 'Tamanho Plus-Size'),
            (26, 'Pijama Masculino Plus Size Homer Simpson Manga Curta Amarelo', 49.90, 'Tamanho Plus-Size')
        ])

    conn.commit()
    conn.close()

# Rota para a página inicial
@app.route('/')
def homepage():
    return render_template("index.html")

# Rota para a página de produtos femininos
@app.route('/feminino')
def feminino():
    return render_template("feminino.html")

# Rota para a página de produtos masculinos
@app.route('/masculino')
def masculino():
    return render_template("masculino.html")

# Rota para a página de produtos infantis
@app.route('/infantil')
def infantil():
    return render_template("infantil.html")

# Rota para a página de produtos plus size
@app.route('/plus-size')
def plusSize():
    return render_template("plus-size.html")


@app.route('/pesquisar', methods=['GET'])
def pesquisar():
    search_term = request.args.get('search_term', '').strip()  # Obtém o termo de pesquisa
    
    if not search_term:
        return redirect('/')  # Se o termo estiver vazio, redireciona para a página inicial

    try:
        # Consulta SQL para buscar produtos com o nome que contenha o termo de pesquisa
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM Produto WHERE nome LIKE ?
        ''', ('%' + search_term + '%',))
        # Obtém os resultados da pesquisa
        produtos_encontrados = cursor.fetchall()

        # Exibe os resultados da pesquisa no template
        return render_template('pesquisa.html', search_term=search_term, produtos=produtos_encontrados)

    except sqlite3.Error as e:
        return f"Erro ao realizar a pesquisa: {str(e)}"

# Rota para a página de compras
@app.route('/comprar', methods=['GET', 'POST'])
def comprar():
    if request.method == 'POST':
        nome = request.form['name']
        email = request.form['email']
        nTelefone = request.form['telefone']
        cep = request.form['cep']
        nCasa = request.form['nCasa']
        idproduto = request.form['idproduto']
        qtd = request.form['quantidade']

        if not nome or not email or not nTelefone or not cep or not nCasa or not idproduto or not qtd:
            return "Erro: Todos os campos são obrigatórios."

        try:
            idproduto = int(idproduto)
            qtd = int(qtd)
        except ValueError:
            return "Erro: Produto e quantidade devem ser valores numéricos."

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('SELECT * FROM conta WHERE nome_sobrenome = ? AND email = ?', (nome, email))
            usuario = cursor.fetchone()
            if not usuario:
                return "Erro: Usuário não encontrado."

            cursor.execute('SELECT * FROM produto WHERE id = ?', (idproduto,))
            produto = cursor.fetchone()
            if not produto:
                return "Erro: Produto não encontrado."

            cursor.execute('''
                INSERT INTO compra (nome, email, nTelefone, cep, nCasa, idproduto, qtd)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (nome, email, nTelefone, cep, nCasa, idproduto, qtd))
            conn.commit()
            return "Compra realizada com sucesso!"
        except sqlite3.IntegrityError as e:
            return f"Erro ao realizar a compra: {str(e)}"
        finally:
            conn.close()

    return render_template('comprar.html')

# Rota para a página de cadastro
@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    if request.method == 'POST':
        nome_sobrenome = request.form['name']
        data_nasc = request.form['dob']
        email = request.form['email']
        senha = request.form['password']

        if not nome_sobrenome or not data_nasc or not email or not senha:
            return "Erro: Todos os campos são obrigatórios."

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return "Erro: Email inválido."

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO conta (nome_sobrenome, data_nasc, email, senha)
                VALUES (?, ?, ?, ?)
            ''', (nome_sobrenome, data_nasc, email, senha))
            conn.commit()
            return "Usuário cadastrado com sucesso!"
        except sqlite3.IntegrityError:
            return "Erro: Este usuário ou email já está cadastrado."
        finally:
            conn.close()

    return render_template('cadastrar.html')

# Rota para a página de login
@app.route('/entrar', methods=['GET', 'POST'])
def entrar():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['password']

        if not email or not senha:
            return "Erro: Todos os campos são obrigatórios."

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('SELECT * FROM conta WHERE email = ? AND senha = ?', (email, senha))
            usuario = cursor.fetchone()
            if usuario:
                return "Usuário encontrado com sucesso!"
            else:
                return "Erro: Usuário ou senha inválidos."
        except sqlite3.Error as e:
            return f"Erro no banco de dados: {str(e)}"
        finally:
            conn.close()

    return render_template("entrar.html")

# Rota para a página de deletar um usuário
@app.route('/deletar', methods=['GET', 'POST'])
def deletar():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['password']

        if not email or not senha:
            return "Erro: Todos os campos são obrigatórios."

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('SELECT * FROM conta WHERE email = ? AND senha = ?', (email, senha))
            usuario = cursor.fetchone()
            if usuario:
                cursor.execute('DELETE FROM conta WHERE email = ? AND senha = ?', (email, senha))
                conn.commit()
                return "Usuário deletado com sucesso!"
            else:
                return "Erro: Usuário não encontrado."
        except sqlite3.Error as e:
            return f"Erro ao deletar usuário: {str(e)}"
        finally:
            conn.close()

    return render_template('deletar.html')

if __name__ == '__main__':
    create_table()
    app.run(debug=True)
