import psycopg2
from psycopg2 import sql
import bcrypt
from pathlib import Path

def Connect_Base():
    try:
        conection = psycopg2.connect(dbname="Arcade_Checkpoint",
                                   host="localhost",
                                   user="postgres",
                                   password="#Gabriel19",
                                   port="5432")
        print("Connetion succeded.")
        return conection
    except psycopg2.OperationalError as e:
        print(f"Error connecting to data base: {e}")
        return None

Connect_Base()

from pathlib import Path

def folks_favorite():
    conn = Connect_Base()

    try:
        with conn.cursor() as cur:
            query = sql.SQL("""
                SELECT 
                    p.ID_PRODUCT,
                    p.NAME_PRODUCT,
                    p.GENRE,
                    p.PLATFORM,
                    p.GAME_MODE,
                    p.PRICE,
                    ROUND(AVG(r.RATING), 2) AS average_rating
                FROM PRODUCT p
                JOIN RATING r ON p.ID_PRODUCT = r.ID_PRODUCT
                GROUP BY p.ID_PRODUCT, p.NAME_PRODUCT, p.GENRE, p.PLATFORM, p.GAME_MODE, p.PRICE
                ORDER BY average_rating DESC
                LIMIT 4;
            """)
            cur.execute(query)
            result = cur.fetchall()

            # Lista com os nomes dos produtos
            names = [row[1] for row in result]

    except Exception as e:
        print(f"Error to find folk's favorites: {e}")
        return [], [], []

    finally:
        conn.close()

    # Buscar imagens na pasta static
    base = Path("C:\\Users\\faust\\Desktop\\Sistema de Recomendação\\static")
    game_titles = []

    for name in names:
        name_lower = name.lower()
        for file in base.iterdir():
            if name_lower in file.stem.lower():  # busca flexível
                game_titles.append(file.name)
                break
        else:
            game_titles.append("default.jpg")  # fallback caso não encontre

    return result, game_titles


def User_Login(Username, Password):
    conn = Connect_Base()

    try:
        with conn.cursor() as cur:
            query = sql.SQL("""
                SELECT c.USERNAME, c.PASSWORD_HASH
                FROM CLIENT c
                WHERE USERNAME = %s 
            """)

            cur.execute(query, (Username,))
            result = cur.fetchone()

            if result:
                stored_username, stored_password = result

                if bcrypt.checkpw(Password.encode('utf-8'), stored_password.encode('utf-8')):
                    print("Login suceded")
                    return True, stored_username  # Retorne True e os dados do usuário para redirecionar ao site
                else:
                    print("Wrong Password")
                    return False, None
                
            else:
                print("Username not found")
                return False, None
            
    except Exception as e:
        print(f"Error trying to Log in: {e}")
        return False, None
    
    finally:
        conn.close()

def Signing_up(Username, Password):
    conn = Connect_Base()
    try:
        with conn.cursor() as cur:
             # Gera o hash da senha com um salt
            Password_hash = bcrypt.hashpw(Password.encode('utf-8'), bcrypt.gensalt())
            # Query para cadastrar usuario
            query = sql.SQL("""INSERT INTO CLIENT(USERNAME, PASSWORD_HASH)
                    VALUES(%s, %s)""")
            
            cur.execute(query, (Username, Password_hash.decode('utf-8')))

            conn.commit()
            return "Sucessfully Signed up User!"
            
    except Exception as e:
        return (f"Error SIgning up User!{e}")
        
    finally:
        conn.close()

def find_prod(product_id):
    conn = Connect_Base()
    product = None
    try:
        with conn.cursor() as cur:
            query = sql.SQL("""
                SELECT 
                    p.ID_PRODUCT,
                    p.NAME_PRODUCT,
                    p.GENRE,
                    p.PLATFORM,
                    p.GAME_MODE,
                    p.PRICE,
                    ROUND(AVG(r.RATING), 2) AS average_rating
                FROM PRODUCT p
                LEFT JOIN RATING r ON p.ID_PRODUCT = r.ID_PRODUCT
                WHERE p.ID_PRODUCT = %s
                GROUP BY p.ID_PRODUCT, p.NAME_PRODUCT, p.GENRE, p.PLATFORM, p.GAME_MODE, p.PRICE
            """)
            cur.execute(query, (product_id,))
            product = cur.fetchone()
    finally:
        conn.close()

    if not product:
        return "Produto não encontrado", 404
    
    # Caminho da pasta de imagens
    base = Path("C:\\Users\\faust\\Desktop\\Sistema de Recomendação\\static")
    game_name = product[1].lower()
    game_title = None

    # Itera pelos arquivos da pasta procurando uma correspondência
    for file in base.iterdir():
        if game_name in file.stem.lower():  # busca por substring (mais flexível)
            game_title = file.name
            break  # achou, não precisa continuar

    if not game_title:
        game_title = "default.jpg"  # fallback caso não encontre nenhuma imagem

    return product, game_title
