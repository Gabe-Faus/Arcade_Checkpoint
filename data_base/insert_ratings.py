import psycopg2
import pandas as pd
from Connect_base import Connect_Base
# ---------- CONFIG ----------
CSV_USERS = r"C:/Users/faust/Desktop/Sistema de Recomendação/fontes/usuarios.csv"
CSV_RATINGS = r"C:/Users/faust/Desktop/Sistema de Recomendação/fontes/matriz_utilidade.csv"
BATCH_USERS = 50   # inserir clientes faltantes em lotes de 50
BATCH_USER_RATINGS = 50  # inserir ratings por 50 usuários por lote
# DB


conn = Connect_Base()
cur = conn.cursor()

# garante que tabela RATING existe
cur.execute("""
CREATE TABLE IF NOT EXISTS RATING (
    ID_CLIENT INT REFERENCES CLIENT(ID_CLIENT),
    ID_PRODUCT INT NOT NULL,
    RATING INT CHECK (RATING BETWEEN 1 AND 5),
    PRIMARY KEY (ID_CLIENT, ID_PRODUCT)
);
""")
conn.commit()

# lê CSVs
df_users = pd.read_csv(CSV_USERS)            # columns: EMAIL, USERNAME, PASSWORD_HASH, SEX, DATE_BIRTH
df_ratings = pd.read_csv(CSV_RATINGS)       # cada linha = avaliações do usuário i, colunas Produto1..ProdutoN

# 1) descobrir quais emails já existem
emails = df_users['EMAIL'].tolist()
if not emails:
    raise SystemExit("Arquivo de usuários vazio.")

placeholders = ','.join(['%s'] * len(emails))
cur.execute(f"SELECT email FROM client WHERE email IN ({placeholders})", emails)
existing = set(r[0] for r in cur.fetchall())

# 2) inserir apenas os usuários faltantes (em lotes)
missing_df = df_users[~df_users['EMAIL'].isin(existing)].reset_index(drop=True)
print(f"Usuarios totais no CSV: {len(df_users)}. Já existentes: {len(existing)}. A inserir: {len(missing_df)}.")

for i in range(0, len(missing_df), BATCH_USERS):
    batch = missing_df.iloc[i:i+BATCH_USERS]
    # montar valores já mogrified para inserir em lote
    vals = []
    for row in batch.itertuples(index=False):
        # atenção: date -> str para evitar problemas de tipo; ajuste se DATE_BIRTH já estiver no formato certo
        vals.append(cur.mogrify("(%s,%s,%s,%s,%s)",
                               (row.EMAIL, row.USERNAME, row.PASSWORD_HASH, row.SEX, str(row.DATE_BIRTH)))
                    .decode('utf-8'))
    sql = "INSERT INTO CLIENT (EMAIL, USERNAME, PASSWORD_HASH, SEX, DATE_BIRTH) VALUES " + ",".join(vals) \
          + " ON CONFLICT (EMAIL) DO NOTHING"
    cur.execute(sql)
    conn.commit()
    print(f"Inseridos clientes {i+1} até {i+len(batch)}")

# 3) buscar mapeamento email -> id_client (agora todos devem existir)
cur.execute(f"SELECT id_client, email FROM client WHERE email IN ({placeholders})", emails)
rows = cur.fetchall()
id_map = {email: idc for (idc, email) in rows}
if len(id_map) != len(emails):
    missing_after = set(emails) - set(id_map.keys())
    raise SystemExit(f"Erro: alguns clientes ainda não estão no DB: {missing_after}")

print("Mapeamento email -> id_client obtido com sucesso.")

# 4) inserir avaliações (RATING) em lotes de usuários
num_users = len(df_ratings)
num_products = df_ratings.shape[1]

for i in range(0, num_users, BATCH_USER_RATINGS):
    block = df_ratings.iloc[i:i+BATCH_USER_RATINGS]
    vals = []
    for local_idx, row in enumerate(block.itertuples(index=False)):
        user_global_idx = i + local_idx  # 0-based
        # pegar email correspondente (presume que usuarios.csv e matriz_utilidade.csv têm a mesma ordem)
        email = df_users.iloc[user_global_idx]['EMAIL']
        id_client = id_map[email]
        for product_id, rating in enumerate(row, start=1):
            vals.append(cur.mogrify("(%s,%s,%s)", (int(id_client), int(product_id), int(rating))).decode('utf-8'))

    if vals:
        sql = ("INSERT INTO RATING (ID_CLIENT, ID_PRODUCT, RATING) VALUES " + ",".join(vals)
               + " ON CONFLICT (ID_CLIENT, ID_PRODUCT) DO UPDATE SET RATING = EXCLUDED.RATING")
        cur.execute(sql)
        conn.commit()
    print(f"✅ Inseridas/atualizadas avaliações para usuários {i+1} até {i+len(block)}")

cur.close()
conn.close()
print("Tudo finalizado com sucesso.")

