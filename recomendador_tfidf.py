# recomendador_tfidf.py
# -*- coding: utf-8 -*-
#Importe as funções em outro script ou rode este arquivo diretamente

from typing import List, Tuple
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from difflib import get_close_matches

def carregar_jogos(csv_path: str) -> pd.DataFrame:
    """Carrega o CSV com os jogos e características.
    Espera colunas: 'Nome', 'Gênero', 'Plataforma', 'Modo de jogo' (nomes flexíveis).
    Retorna um DataFrame com pelo menos estas colunas (normaliza os nomes das colunas)."""

    df = pd.read_csv(csv_path)
    # normalizar nomes de colunas para facilitar uso
    col_map = {c.lower(): c for c in df.columns}
    # tentar mapear colunas comuns em pt-br
    nome_col = next((col_map[k] for k in col_map if 'nome' in k), None)
    genero_col = next((col_map[k] for k in col_map if 'gênero' in k or 'genero' in k), None)
    plataforma_col = next((col_map[k] for k in col_map if 'plataforma' in k), None)
    modo_col = next((col_map[k] for k in col_map if 'modo' in k or 'jogo' in k and 'modo' in k), None)
    # fallback simples se não encontrou
    if nome_col is None:
        raise ValueError(\"Coluna 'Nome' não encontrada no CSV. Verifique cabeçalhos.\")
    if genero_col is None:
        raise ValueError(\"Coluna 'Gênero' não encontrada no CSV. Verifique cabeçalhos.\")
    if plataforma_col is None:
        raise ValueError(\"Coluna 'Plataforma' não encontrada no CSV. Verifique cabeçalhos.\")
    if modo_col is None:
        # tentar encontrar qualquer coluna que contenha 'modo'
        modo_col = next((col_map[k] for k in col_map if 'modo' in k), None)
    if modo_col is None:
        raise ValueError(\"Coluna 'Modo de jogo' não encontrada no CSV. Verifique cabeçalhos.\")
    # renomear colunas para nomes internos padronizados
    df = df.rename(columns={nome_col: 'Nome', genero_col: 'Gênero', plataforma_col: 'Plataforma', modo_col: 'Modo de jogo'})
    return df[['Nome', 'Gênero', 'Plataforma', 'Modo de jogo']].copy()

def limpar_texto(texto: str) -> str:
    """Limpeza simples de texto: remove separadores comuns e normaliza espaços.
    Mantém a acentuação para preservar termos em pt-br, mas colocamos tudo em minúsculas."""

    if pd.isna(texto):
        return ''
    txt = str(texto)
    # substituir barras, vírgulas e parênteses por espaço
    for ch in ['/', ',', ';', '(', ')', ':']:
        txt = txt.replace(ch, ' ')
    # substituir múltiplos espaços por um só e strip
    txt = ' '.join(txt.split())
    return txt.lower()

def criar_descricoes(df: pd.DataFrame) -> pd.DataFrame:
    """Cria a coluna 'descricao' concatenando Gênero + Plataforma + Modo de jogo.
    Aplica limpeza básica usando limpar_texto."""
    
    df = df.copy()
    df['Gênero'] = df['Gênero'].fillna('').astype(str)
    df['Plataforma'] = df['Plataforma'].fillna('').astype(str)
    df['Modo de jogo'] = df['Modo de jogo'].fillna('').astype(str)
    df['descricao'] = df.apply(lambda r: r['Gênero'] + ' ' + r['Plataforma'] + ' ' + r['Modo de jogo'], axis=1)
    df['descricao'] = df['descricao'].apply(limpar_texto)
    return df

def construir_tfidf(descricoes: List[str], ngram_range=(1,2)) -> Tuple[TfidfVectorizer, np.ndarray]:
    """Cria um TfidfVectorizer e transforma as descrições em matriz TF-IDF.
    Retorna o vectorizer treinado e a matriz TF-IDF (sparse matrix).
    ngram_range pode ser ajustado; (1,2) permite uni- e bi-gramas para captar combos tipo 'mundo aberto'."""

    vectorizer = TfidfVectorizer(ngram_range=ngram_range)
    tfidf_matrix = vectorizer.fit_transform(descricoes)
    return vectorizer, tfidf_matrix

def calcular_similaridade(tfidf_matrix) -> np.ndarray:
    """Calcula similaridade por cosseno entre todas as linhas da matriz TF-IDF.
    Retorna uma matriz (numpy array) quadrada com valores entre 0 e 1."""

    sim = cosine_similarity(tfidf_matrix)
    return sim

def _achar_indice_jogo(df: pd.DataFrame, nome_jogo: str) -> int:
    """Tenta localizar o índice do jogo dado seu nome.
    Procura por correspondência exata.
    Tenta correspondência case-insensitive.
    Usa get_close_matches para sugerir nomes semelhantes (fuzzy).
    Levanta ValueError se não encontrar nenhum candidato.
    Retorna o índice (inteiro) da primeira correspondência encontrada."""

    nomes = df['Nome'].tolist()
    # tentativa exata
    if nome_jogo in nomes:
        return nomes.index(nome_jogo)
    # tentativa case-insensitive
    lower_map = {n.lower(): i for i, n in enumerate(nomes)}
    if nome_jogo.lower() in lower_map:
        return lower_map[nome_jogo.lower()]
    # tentativa fuzzy (difflib)
    matches = get_close_matches(nome_jogo, nomes, n=3, cutoff=0.5)
    if matches:
        # retornar o índice do melhor match
        return nomes.index(matches[0])
    raise ValueError(f\"Jogo '{nome_jogo}' não encontrado. Sugestões: {matches}\")

def recomendar(jogo: str, df: pd.DataFrame, similarity_matrix: np.ndarray, top_n: int = 5, incluir_score: bool = False) -> List:
    """Retorna os top_n jogos mais similares ao 'jogo' informado.
    'jogo' pode ser o nome completo ou aproximação (usa fuzzy matching).
    Retorna lista de nomes (ou tuplas (nome, score) se incluir_score=True)."""

    idx = _achar_indice_jogo(df, jogo)
    # pegar os scores de similaridade do jogo com todos os outros
    scores = list(enumerate(similarity_matrix[idx]))
    # ordenar por score decrescente (mantendo o próprio jogo em primeiro lugar)
    scores = sorted(scores, key=lambda x: x[1], reverse=True)
    # filtrar para remover o próprio jogo (primeiro elemento)
    resultados = []
    for i, score in scores:
        if i == idx:
            continue
        resultados.append((df.at[i, 'Nome'], float(score)))
        if len(resultados) >= top_n:
            break
    if incluir_score:
        return resultados
    else:
        return [r[0] for r in resultados]

# Função que junta o pipeline completo (para conveniência)
def pipeline_recomendador(csv_path: str, ngram_range=(1,2)) -> Tuple[pd.DataFrame, TfidfVectorizer, np.ndarray]:
    """Roda todo o pipeline: carregar dados -> criar descricoes -> TF-IDF -> similaridade.
    Retorna: df (com coluna 'descricao'), vectorizer, similarity_matrix"""

    df = carregar_jogos(csv_path)
    df = criar_descricoes(df)
    vectorizer, tfidf_matrix = construir_tfidf(df['descricao'].tolist(), ngram_range=ngram_range)
    sim_matrix = calcular_similaridade(tfidf_matrix)
    return df, vectorizer, sim_matrix

if __name__ == \"__main__\":
    # Demonstração rápida caso rode o script diretamente.
    import os
    csv_default = 'jogos_carac.csv'  # altere se o arquivo estiver em outro local
    if not os.path.exists(csv_default):
        print(f\"Arquivo padrão '{csv_default}' não encontrado. Passe o caminho para o CSV.\")
    else:
        print(\"Carregando dados e rodando pipeline de recomendação...\")
        df, vectorizer, sim = pipeline_recomendador(csv_default)
        print(f\"Foram carregados {len(df)} jogos.\")
        exemplo = df.loc[0, 'Nome']
        print(f\"Exemplo: recomendações para -> {exemplo}\")
        recs = recomendar(exemplo, df, sim, top_n=5, incluir_score=True)
        for nome, sc in recs:
            print(f\"  - {nome} (score {sc:.3f})\")
