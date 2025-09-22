import pandas as pd
import random
import hashlib
from faker import Faker

fake = Faker()

num_usuarios = 500

usuarios = []
for i in range(num_usuarios):
    email = f"user{i+1}@example.com"
    username = f"user{i+1}"
    
    # senha simples + hash SHA256 (só para simulação)
    password = f"senha{i+1}"
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    sex = random.choice(['M', 'F'])
    date_birth = fake.date_of_birth(minimum_age=18, maximum_age=70)
    
    usuarios.append([email, username, password_hash, sex, date_birth])

df_usuarios = pd.DataFrame(usuarios, columns=["EMAIL", "USERNAME", "PASSWORD_HASH", "SEX", "DATE_BIRTH"])
df_usuarios.to_csv("usuarios.csv", index=False)