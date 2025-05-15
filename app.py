
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime, date
from calendar import monthrange



# Valida a data no formulário
def validar_data(data_str):
    try:
        data = datetime.strptime(data_str, '%Y-%m-%d')  # Garante o formato 'YYYY-MM-DD'
        return data
    except ValueError:
        return None


app = Flask(__name__)


# função para conectar o banco de dados

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    #conn.execute('''ALTER TABLE clientes ADD service TEXT'''), ''''''''comentei porque já inseri esse campo no banco'''''''
    return conn

# criar a tabela se nao existir clientes

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            idade TEXT NOT NULL,
            data_cadastro DATE NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html', titulo="index")

@app.route('/listagem.html')
def listagem ():
    conn = get_db_connection()
    clientes = conn.execute('SELECT * FROM clientes').fetchall()
    conn.close()
    return render_template('listagem.html', clientes=clientes)


@app.route('/saiba_mais')
def saiba_mais():
    return render_template('saiba_mais.html', titulo="Saiba Mais")


@app.route('/contato')
def contato():
    return render_template('contato.html', titulo="Contato")

@app.route('/agenda')
def agenda():
    conn = get_db_connection()
    clientes = conn.execute('SELECT nome, data_cadastro FROM clientes').fetchall()
    conn.close()

    # Convertendo as informações para o formato JSON que será usado no template
    eventos = []
    for cliente in clientes:
        eventos.append({
            "title": cliente['nome'],  # Nome do cliente
            "start": cliente['data_cadastro'],# Data de cadastro no formato YYYY-MM-DD

        })
    return render_template('agenda.html', titulo="Agenda", eventos=eventos)



@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    if request.method == 'POST':
        nome = request.form['nome']
        idade = request.form['idade']
        data_cadastro = request.form['data_cadastro']
        servico = request.form['servico']
        conn = get_db_connection()
        conn.execute('INSERT INTO clientes (nome, idade, data_cadastro, servico) VALUES (?, ?, ?, ?)', (nome, idade, data_cadastro, servico))
        conn.commit()
        conn.close()
        return redirect(url_for('index') + '?sucesso=1')
    return render_template('form.html', titulo='Adicionar Pacientes')

@app.route('/editar/<int:index>', methods=['GET', 'POST'])
def editar(index):
    if request.method == 'POST':
        conn = get_db_connection()
        conn.execute('UPDATE clientes SET nome = ?, idade = ?, data_cadastro = ?, servico = ? WHERE id = ?',
                     (request.form['nome'], request.form['idade'], request.form['data_cadastro'], request.form['servico'], index))
        conn.commit()
        conn.close()
        return redirect(url_for('index') + '?editado=1')
    conn = get_db_connection()
    cliente = conn.execute('SELECT * FROM clientes WHERE id = ?', (index,)).fetchone()
    conn.close()
    return render_template('form.html', titulo='Editar Cliente', cliente=cliente)

@app.route('/excluir/<int:index>')
def excluir(index):
    conn = get_db_connection()
    conn.execute('DELETE FROM clientes WHERE id = ?', (index,))
    conn.commit()
    conn.close()
    return redirect(url_for('index') + '?excluido=1')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)

