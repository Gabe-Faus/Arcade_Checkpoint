import psycopg2
import pandas as pd
from Data_base import Connect_Base

# conecta no banco
conn = Connect_Base()

cur = conn.cursor()

# lê CSV
df = pd.read_csv(r"C:\Users\faust\Desktop\Sistema de Recomendação\usuarios.csv")

# insere linha por linha
for row in df.itertuples(index=False):
    cur.execute("""
        #INSERT INTO CLIENT (EMAIL, USERNAME, PASSWORD_HASH, SEX, DATE_BIRTH)
        #VALUES (%s, %s, %s, %s, %s)
""", (row.EMAIL, row.USERNAME, row.PASSWORD_HASH, row.SEX, row.DATE_BIRTH))

conn.commit()
cur.close()
conn.close()