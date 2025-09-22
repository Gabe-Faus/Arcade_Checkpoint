import pandas as pd 
matriz = pd.read_csv("fontes\matriz_utilidade.csv")

for user_id, row in enumerate(matriz.itertuples(index=False), start=1):
    for product_id, rating in enumerate(row, start=1):
        print(f"INSERT INTO RATING (ID_CLIENT, ID_PRODUCT, RATING) VALUES ({user_id}, {product_id}, {rating});")