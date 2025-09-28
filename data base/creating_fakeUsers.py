import pandas as pd
import random
import hashlib
from faker import Faker

fake = Faker()

num_usuarios = 500

usuarios = []
for i in range(num_usuarios):
    username = f"user{i+1}"
    
    # senha simples + hash SHA256 (só para simulação)
    password = f"senha{i+1}"
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    

    
    usuarios.append([username, password_hash])

df_usuarios = pd.DataFrame(usuarios, columns=["USERNAME", "PASSWORD_HASH"])
df_usuarios.to_csv("usuarios.csv", index=False)