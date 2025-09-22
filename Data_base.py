import psycopg2

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

Connect_Base();