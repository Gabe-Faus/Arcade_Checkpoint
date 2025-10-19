from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify, session
import psycopg2
from psycopg2 import sql
import io
from io import BytesIO
from Connect_base import *
from pathlib import Path

app = Flask(__name__)

app.secret_key = '#G@br!el19'


# Original Route
@app.route("/")
def raiz():
    return redirect(url_for('login'))

@app.route('/Home_page')
def home_page():
    all, game_titles = all_games()
    combined = list(zip(all, game_titles))
    return render_template('Home_page.html', all=all, game_titles=game_titles, combined=combined)

# Sign up Route
@app.route('/Sign_up', methods=['GET', 'POST'])
def Sign_up():
    if request.method == 'POST':
        Username = request.form['Username']
        Password = request.form['Password']

        try:
            Signing_up(Username, Password)
            return redirect(url_for('Test'))
        
        except Exception as e:
            mensagem = f'Error Signing up user: {e}'

            return render_template('Sign_up.html', mensagem=mensagem)

    return render_template('Sign_up.html')


#Log in Route
@app.route('/Log_in', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        Username = request.form['Username']
        Password = request.form['Password']
        
        try:
            # Chama a função Login do arquivo Usuario.py
            sucesso, stored_username = User_Login(Username, Password)
            print(sucesso)

            if sucesso:
                print(sucesso)
                # Login bem-sucedido, salvar os dados do usuário na sessão
                session['logged_in_user'] = stored_username  # Armazena o nome do usuário na sessão
                return redirect(url_for('home_page'))  # Redireciona para a página do usuário
            else:
                mensagem = 'Invalid Username or Password'
        except Exception as e:
            mensagem = f'Error trying to log in: {e}'
        
        return render_template('Log_in.html', mensagem=mensagem)  # Retorna à página de login com mensagem de erro
    
    return render_template('Log_in.html')  # Página de login para requisições GET

# Product Page Route
@app.route('/product/<int:product_id>')
def product_page(product_id):
    product, game_title = find_prod(product_id)
    return render_template("Product_page.html", product=product, game_title=game_title)


# Test Route
@app.route('/Test')
def Test():
    return render_template('Test.html')

@app.route('/search')
def search():
    term = request.args.get("q", "").strip()

    if not term:
        return render_template("Search_results.html", results=[], query=term)

    results, game_titles = search_games(term)
    combined = list(zip(results, game_titles))
    
    return render_template("Search_results.html", results=combined, query=term)


# MAIN
if __name__ ==  "__main__":
     app.run(debug=True, port=5001)  # Alterar o número da porta para 5001 ou outra porta disponível

