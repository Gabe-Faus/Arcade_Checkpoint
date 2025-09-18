
import numpy as np
import pandas as pd

num_usuarios = 500
num_produtos = 20

# Avaliação aleatória entre 1 e 5 usando NUMPY
matriz_utilidade = np.random.randint(1, 6, size=(num_usuarios, num_produtos))

# Criação do arquivo csv usando PANDAS
df = pd.DataFrame(matriz_utilidade, columns=[f'Produto{i+1}' for i in range(num_produtos)])
df.to_csv('matriz_utilidade.csv', index=False)
