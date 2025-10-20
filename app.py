from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify, session
import psycopg2
from psycopg2 import sql
import io
from io import BytesIO
from Connect_base import *
from pathlib import Path
from recomendador_tfidf import *

app = Flask(__name__)

app.secret_key = '#G@br!el19'

sistema = inicializar_sistema()

# Original Route
@app.route("/")
def raiz():
    return redirect(url_for('login'))

# Home page Route
@app.route('/Home_page')
def home_page():
    try:
        preferencias_usuario = session.get('preferencias') 
        if not preferencias_usuario:
            print("Nenhuma preferência encontrada. Redirecionando...")
            return redirect(url_for('index'))  
        resultado = gerar_recomendacoes(sistema, preferencias_usuario, num_recomendacoes=10)

        if not resultado["sucesso"]:
            return render_template("Home_page.html", erro=resultado["erro"])

        nomes_recomendados = [rec["nome"] for rec in resultado["recomendacoes"]]
        print("Jogos recomendados:", nomes_recomendados)

        jogos_banco, imagens = all_games(filtros=nomes_recomendados)

        combined = list(zip(jogos_banco, imagens))

        return render_template('Home_page.html',
                               recomendacoes=resultado["recomendacoes"],
                               combined=combined)

    except Exception as e:
        print("Erro ao processar home:", e)
        return render_template("Home_page.html", erro=str(e))

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
            sucesso, stored_username = User_Login(Username, Password)
            print(sucesso)

            if sucesso:
                print(sucesso)
                session['logged_in_user'] = stored_username  
                return redirect(url_for('home_page'))  
            else:
                mensagem = 'Invalid Username or Password'
        except Exception as e:
            mensagem = f'Error trying to log in: {e}'
        
        return render_template('Log_in.html', mensagem=mensagem)  
    
    return render_template('Log_in.html')  

# Product Page Route
@app.route('/product/<int:product_id>')
def product_page(product_id):
    product, game_title = find_prod(product_id)
    return render_template("Product_page.html", product=product, game_title=game_title)


# Test Route
@app.route('/Test')
def Test():
    return render_template('Test.html')

# Search Route
@app.route('/search')
def search():
    term = request.args.get("q", "").strip()

    if not term:
        return render_template("Search_results.html", results=[], query=term)

    results, game_titles = search_games(term)
    combined = list(zip(results, game_titles))
    
    return render_template("Search_results.html", results=combined, query=term)

# Form Route
@app.route('/salvar_respostas', methods=['POST'])
def salvar_respostas():
    try:
        preferencias_usuario = request.get_json()
        session['preferencias'] = preferencias_usuario 
        print("Preferências salvas:", preferencias_usuario)

        return jsonify({"redirect": url_for('home_page')})  

    except Exception as e:
        print("Erro ao salvar respostas:", e)
        return jsonify({"erro": str(e)}), 500

# MAIN
if __name__ ==  "__main__":
     app.run(debug=True, port=5001)  # Alterar o número da porta para 5001 ou outra porta disponível

