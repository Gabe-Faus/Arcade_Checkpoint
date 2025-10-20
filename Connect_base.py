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

def all_games(filtros=None):
    conn = Connect_Base()

    try:
        with conn.cursor() as cur:
            if filtros and len(filtros) > 0:
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
                    WHERE p.NAME_PRODUCT = ANY(%s)
                    GROUP BY p.ID_PRODUCT, p.NAME_PRODUCT, p.GENRE, p.PLATFORM, p.GAME_MODE, p.PRICE
                    ORDER BY average_rating DESC;
                """)
                cur.execute(query, (filtros,))
            else:
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
                    ORDER BY average_rating DESC;
                """)
                cur.execute(query)

            result = cur.fetchall()
            names = [row[1] for row in result]

    except Exception as e:
        print(f"❌ Erro ao buscar jogos: {e}")
        return [], []

    finally:
        conn.close()

    base = Path("C:\\Users\\faust\\Desktop\\Sistema de Recomendação\\static")
    game_titles = []

    for name in names:
        name_lower = name.lower()
        for file in base.iterdir():
            if name_lower in file.stem.lower():
                game_titles.append(file.name)
                break
        else:
            game_titles.append("default.jpg")

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
                    return True, stored_username  
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
            Password_hash = bcrypt.hashpw(Password.encode('utf-8'), bcrypt.gensalt())
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
    
    base = Path("C:\\Users\\faust\\Desktop\\Sistema de Recomendação\\static")
    game_name = product[1].lower()
    game_title = None

    for file in base.iterdir():
        if game_name in file.stem.lower(): 
            game_title = file.name
            break  

    if not game_title:
        game_title = "default.jpg"  

    return product, game_title

def search_games(term):
    conn = Connect_Base()
    try:
        with conn.cursor() as cur:
            query = sql.SQL("""
                SELECT 
                    id_product,
                    name_product,
                    genre,
                    platform,
                    game_mode,
                    price
                FROM product
                WHERE LOWER(name_product) LIKE LOWER(%s)
                OR LOWER(genre) LIKE LOWER(%s)
                OR LOWER(platform) LIKE LOWER(%s)
                ORDER BY name_product;
            """)
            cur.execute(query, (f"%{term}%", f"%{term}%", f"%{term}%"))
            results = cur.fetchall()
            names = [row[1] for row in results]


    except Exception as e:
        print(f"Erro ao buscar: {e}")
        results = []
    finally:
        conn.close()

    base = Path("C:\\Users\\faust\\Desktop\\Sistema de Recomendação\\static")
    game_titles = []

    for name in names:
        name_lower = name.lower()
        for file in base.iterdir():
            if name_lower in file.stem.lower(): 
                game_titles.append(file.name)
                break
        else:
            game_titles.append("default.jpg")

    return results, game_titles