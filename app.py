from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify, session
import psycopg2
from psycopg2 import sql
import io
from io import BytesIO

app = Flask(__name__)

app.secret_key = '#G@br!el19'


# Original Route
@app.route("/")
def raiz():
    return redirect(url_for('home_page'))

@app.route('/Home_page')
def home_page():
    return render_template('Home_page.html')

# Sign up Route
@app.route('/Sign_up', methods=['GET', 'POST'])
def Sign_up():
    if request.method == 'POST':
        nome = request.form['nome']
        Senha = request.form['Senha']
        Email = request.form['Email']
        Data_Nasc = request.form['Data_Nasc']
        Sexo = request.form['Sexo']

        # Lida com o arquivo de foto
        Foto = request.files['Foto']
        foto_bytes = Foto.read()  # Converte a foto para bytes para armazenar no banco de dados

        try:
            # Aqui, 'foto_bytes' seria passado para a função de Cadastro
            Cadastro(nome, Senha, Email, Data_Nasc, Sexo, foto_bytes)
            return redirect(url_for('login'))
        except Exception as e:
            mensagem = f'Erro ao cadastrar usuário: {e}'
            return render_template('Sign_up.html', mensagem=mensagem)

        

    return render_template('Sign_up.html')

# Submit form Route
@app.route('/submit_form', methods=['POST'])
def submit_form():
    # Aqui você processa os dados do formulário
    nome = request.form['nome']
    email = request.form['email']
    
    # Se o processamento for bem-sucedido, redireciona para a página de login
    return redirect(url_for('Log_in'))

#Log in Route
@app.route('/Log_in', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        Email = request.form['Email']
        Senha = request.form['Senha']
        
        try:
            # Chama a função Login do arquivo Usuario.py
            sucesso, nome_usuario = UsuarioLogin(Email, Senha)
            print(sucesso)

            if sucesso:
                print(sucesso)
                # Login bem-sucedido, salvar os dados do usuário na sessão
                session['usuario_logado'] = nome_usuario  # Armazena o nome do usuário na sessão
                return redirect(url_for('pagina_usuario_1'))  # Redireciona para a página do usuário
            else:
                mensagem = 'Email ou Senha inválidos'
        except Exception as e:
            mensagem = f'Ocorreu um erro ao tentar logar: {e}'
        
        return render_template('Log_in.html', mensagem=mensagem)  # Retorna à página de login com mensagem de erro
    
    return render_template('Log_in.html')  # Página de login para requisições GET

# MAIN
if __name__ ==  "__main__":
     app.run(debug=True, port=5001)  # Alterar o número da porta para 5001 ou outra porta disponível


