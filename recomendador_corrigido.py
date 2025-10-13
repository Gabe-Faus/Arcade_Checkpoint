# -*- coding: utf-8 -*-
"""
Sistema de Recomendação de Jogos usando TF-IDF e Similaridade de Cosseno
Versão corrigida com tratamento robusto de índices e melhor manipulação de dados
"""

from typing import List, Tuple, Optional
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from difflib import get_close_matches

def carregar_jogos(csv_path: str) -> pd.DataFrame:
    """
    Carrega o CSV com os jogos e características.
    Espera colunas: 'Nome', 'Gênero', 'Plataforma', 'Modo de jogo'.
    
    CORREÇÃO IMPORTANTE: Agora reseta os índices do DataFrame para garantir
    que sejam sequenciais (0, 1, 2, ...), evitando problemas ao acessar dados
    por posição posteriormente.
    """
    df = pd.read_csv(csv_path)
    
    # Criar mapeamento de colunas em minúsculas para facilitar busca
    col_map = {c.lower(): c for c in df.columns}
    
    # Buscar colunas usando palavras-chave (com lógica corrigida)
    nome_col = next((col_map[k] for k in col_map if 'nome' in k), None)
    
    # CORREÇÃO: Separar lógica para gênero/genero (com e sem acento)
    genero_col = next((col_map[k] for k in col_map if 'gênero' in k or 'genero' in k), None)
    
    plataforma_col = next((col_map[k] for k in col_map if 'plataforma' in k), None)
    
    # CORREÇÃO: Melhorar a lógica de detecção da coluna de modo
    # Procura por colunas que contenham 'modo' OU que contenham ambos 'modo' E 'jogo'
    modo_col = next((col_map[k] for k in col_map 
                     if 'modo' in k or ('modo' in k and 'jogo' in k)), None)
    
    # Validação de colunas obrigatórias com mensagens mais claras
    if nome_col is None:
        raise ValueError(
            f"Coluna 'Nome' não encontrada no CSV.\n"
            f"Colunas disponíveis: {list(df.columns)}"
        )
    if genero_col is None:
        raise ValueError(
            f"Coluna 'Gênero' não encontrada no CSV.\n"
            f"Colunas disponíveis: {list(df.columns)}"
        )
    if plataforma_col is None:
        raise ValueError(
            f"Coluna 'Plataforma' não encontrada no CSV.\n"
            f"Colunas disponíveis: {list(df.columns)}"
        )
    if modo_col is None:
        raise ValueError(
            f"Coluna 'Modo de jogo' não encontrada no CSV.\n"
            f"Colunas disponíveis: {list(df.columns)}"
        )
    
    # Renomear colunas para nomes internos padronizados
    df = df.rename(columns={
        nome_col: 'Nome',
        genero_col: 'Gênero',
        plataforma_col: 'Plataforma',
        modo_col: 'Modo de jogo'
    })
    
    # Selecionar apenas as colunas necessárias
    df = df[['Nome', 'Gênero', 'Plataforma', 'Modo de jogo']].copy()
    
    # CORREÇÃO CRÍTICA: Resetar índices para garantir sequência 0, 1, 2, ...
    # Isso é essencial para que as operações de indexação funcionem corretamente
    df = df.reset_index(drop=True)
    
    # Remover linhas onde o Nome está vazio (jogos inválidos)
    df = df[df['Nome'].notna() & (df['Nome'].str.strip() != '')].copy()
    df = df.reset_index(drop=True)
    
    return df

def limpar_texto(texto: str) -> str:
    """
    Limpeza e normalização de texto para melhorar a qualidade do TF-IDF.
    Remove separadores, normaliza espaços e converte para minúsculas.
    Preserva acentuação para manter termos em português corretos.
    """
    if pd.isna(texto):
        return ''
    
    txt = str(texto).strip()
    
    # Substituir separadores comuns por espaço
    separadores = ['/', ',', ';', '(', ')', ':', '-', '|']
    for sep in separadores:
        txt = txt.replace(sep, ' ')
    
    # Normalizar múltiplos espaços em um único espaço
    txt = ' '.join(txt.split())
    
    return txt.lower()

def criar_descricoes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cria a coluna 'descricao' concatenando Gênero + Plataforma + Modo de jogo.
    CORREÇÃO: Adiciona tratamento para jogos com descrições vazias e aviso.
    """
    df = df.copy()
    
    # Preencher valores vazios e converter para string
    df['Gênero'] = df['Gênero'].fillna('').astype(str)
    df['Plataforma'] = df['Plataforma'].fillna('').astype(str)
    df['Modo de jogo'] = df['Modo de jogo'].fillna('').astype(str)
    
    # Criar descrição concatenada
    df['descricao'] = df.apply(
        lambda r: f"{r['Gênero']} {r['Plataforma']} {r['Modo de jogo']}", 
        axis=1
    )
    
    # Aplicar limpeza de texto
    df['descricao'] = df['descricao'].apply(limpar_texto)
    
    # CORREÇÃO: Verificar e avisar sobre descrições vazias
    descricoes_vazias = df[df['descricao'].str.strip() == '']
    if len(descricoes_vazias) > 0:
        print(f"AVISO: {len(descricoes_vazias)} jogo(s) com descrição vazia:")
        for idx, nome in descricoes_vazias['Nome'].items():
            print(f"  - {nome}")
        print("Esses jogos podem gerar recomendações imprecisas.\n")
    
    return df

def construir_tfidf(descricoes: List[str], ngram_range=(1, 2)) -> Tuple[TfidfVectorizer, np.ndarray]:
    """
    Cria um TfidfVectorizer e transforma as descrições em matriz TF-IDF.
    
    O ngram_range=(1,2) permite capturar tanto palavras individuais quanto
    pares de palavras consecutivas (por exemplo: 'mundo' e 'mundo aberto'),
    o que melhora a qualidade das recomendações para características compostas.
    
    CORREÇÃO: Adiciona parâmetros para melhor tratamento de texto em português.
    """
    vectorizer = TfidfVectorizer(
        ngram_range=ngram_range,
        min_df=1,  # Mínimo de documentos para uma palavra ser considerada
        max_df=0.95,  # Ignora palavras que aparecem em mais de 95% dos documentos
        strip_accents=None  # Mantém acentos para preservar semântica do português
    )
    
    tfidf_matrix = vectorizer.fit_transform(descricoes)
    
    return vectorizer, tfidf_matrix

def calcular_similaridade(tfidf_matrix) -> np.ndarray:
    """
    Calcula similaridade por cosseno entre todas as linhas da matriz TF-IDF.
    Retorna uma matriz quadrada onde cada célula [i,j] representa a similaridade
    entre o jogo i e o jogo j (valores entre 0 e 1).
    """
    sim = cosine_similarity(tfidf_matrix)
    return sim

def _achar_indice_jogo(df: pd.DataFrame, nome_jogo: str) -> int:
    """
    Localiza o índice do jogo no DataFrame dado seu nome.
    
    CORREÇÃO IMPORTANTE: Agora trabalha corretamente com índices do DataFrame,
    assumindo que eles foram resetados (0, 1, 2, ...) na função carregar_jogos.
    
    Estratégia de busca em três níveis:
    1. Correspondência exata (case-sensitive)
    2. Correspondência case-insensitive
    3. Busca fuzzy usando diflib (para nomes aproximados)
    """
    # CORREÇÃO: Trabalhar diretamente com os índices do DataFrame
    # ao invés de converter para lista e usar .index()
    
    # Nível 1: Tentativa de correspondência exata
    match_exato = df[df['Nome'] == nome_jogo]
    if not match_exato.empty:
        return match_exato.index[0]
    
    # Nível 2: Tentativa case-insensitive
    match_insensitive = df[df['Nome'].str.lower() == nome_jogo.lower()]
    if not match_insensitive.empty:
        return match_insensitive.index[0]
    
    # Nível 3: Busca fuzzy (aproximada)
    nomes = df['Nome'].tolist()
    matches = get_close_matches(nome_jogo, nomes, n=5, cutoff=0.6)
    
    if matches:
        melhor_match = matches[0]
        print(f"Jogo '{nome_jogo}' não encontrado exatamente.")
        print(f"Usando '{melhor_match}' como melhor correspondência.")
        if len(matches) > 1:
            print(f"Outras sugestões: {', '.join(matches[1:])}")
        
        # Retornar índice do melhor match
        return df[df['Nome'] == melhor_match].index[0]
    
    # Se nenhuma correspondência foi encontrada
    raise ValueError(
        f"Jogo '{nome_jogo}' não encontrado no banco de dados.\n"
        f"Total de jogos disponíveis: {len(df)}\n"
        f"Verifique a grafia ou liste os jogos disponíveis."
    )

def recomendar(
    jogo: str,
    df: pd.DataFrame,
    similarity_matrix: np.ndarray,
    top_n: int = 5,
    incluir_score: bool = False,
    score_minimo: Optional[float] = None
) -> List:
    """
    Retorna os top_n jogos mais similares ao 'jogo' informado.
    
    CORREÇÃO IMPORTANTE: Agora usa iloc para acessar dados por posição,
    garantindo que funcione corretamente independente dos índices do DataFrame.
    
    Parâmetros adicionados:
    - score_minimo: filtra recomendações com similaridade abaixo deste valor
    """
    # Encontrar índice do jogo (com busca fuzzy integrada)
    idx = _achar_indice_jogo(df, jogo)
    
    # Obter scores de similaridade do jogo com todos os outros
    scores = list(enumerate(similarity_matrix[idx]))
    
    # Ordenar por score decrescente
    scores = sorted(scores, key=lambda x: x[1], reverse=True)
    
    # Coletar recomendações (excluindo o próprio jogo)
    resultados = []
    for i, score in scores:
        # Pular o próprio jogo
        if i == idx:
            continue
        
        # Aplicar filtro de score mínimo se especificado
        if score_minimo is not None and score < score_minimo:
            continue
        
        # CORREÇÃO CRÍTICA: Usar iloc para acesso posicional
        nome_jogo = df.iloc[i]['Nome']
        resultados.append((nome_jogo, float(score)))
        
        # Parar quando atingir o número desejado
        if len(resultados) >= top_n:
            break
    
    # Retornar formato adequado conforme solicitado
    if incluir_score:
        return resultados
    else:
        return [r[0] for r in resultados]

def listar_jogos(df: pd.DataFrame, limite: int = 20) -> None:
    """
    Função auxiliar para listar jogos disponíveis no banco de dados.
    Útil para o usuário descobrir nomes exatos dos jogos.
    """
    print(f"\n{'='*60}")
    print(f"Total de jogos no banco: {len(df)}")
    print(f"Mostrando os primeiros {min(limite, len(df))} jogos:")
    print(f"{'='*60}")
    
    for idx, nome in enumerate(df['Nome'].head(limite), 1):
        print(f"{idx:3d}. {nome}")
    
    if len(df) > limite:
        print(f"\n... e mais {len(df) - limite} jogos.")
    print(f"{'='*60}\n")

def pipeline_recomendador(
    csv_path: str,
    ngram_range=(1, 2)
) -> Tuple[pd.DataFrame, TfidfVectorizer, np.ndarray]:
    """
    Executa todo o pipeline de recomendação de forma integrada.
    
    Pipeline completo:
    1. Carrega dados do CSV (com reset de índices)
    2. Cria descrições concatenadas e limpas
    3. Gera matriz TF-IDF
    4. Calcula matriz de similaridade
    
    Retorna: (DataFrame processado, Vectorizer treinado, Matriz de similaridade)
    """
    print("Iniciando pipeline de recomendação...\n")
    
    print("1. Carregando dados do CSV...")
    df = carregar_jogos(csv_path)
    print(f"   ✓ {len(df)} jogos carregados com sucesso.\n")
    
    print("2. Criando descrições dos jogos...")
    df = criar_descricoes(df)
    print(f"   ✓ Descrições criadas.\n")
    
    print("3. Construindo modelo TF-IDF...")
    vectorizer, tfidf_matrix = construir_tfidf(
        df['descricao'].tolist(),
        ngram_range=ngram_range
    )
    print(f"   ✓ Matriz TF-IDF criada: {tfidf_matrix.shape}\n")
    
    print("4. Calculando similaridades...")
    sim_matrix = calcular_similaridade(tfidf_matrix)
    print(f"   ✓ Matriz de similaridade calculada: {sim_matrix.shape}\n")
    
    print("Pipeline concluído com sucesso!\n")
    
    return df, vectorizer, sim_matrix

if __name__ == "__main__":
    """
    Demonstração de uso do sistema de recomendação.
    """
    import os
    
    csv_default = 'jogos_carac.csv'
    
    if not os.path.exists(csv_default):
        print(f"ERRO: Arquivo '{csv_default}' não encontrado.")
        print("Por favor, certifique-se de que o arquivo CSV está no mesmo diretório.")
    else:
        try:
            # Executar pipeline completo
            df, vectorizer, sim = pipeline_recomendador(csv_default)
            
            # Listar alguns jogos disponíveis
            listar_jogos(df, limite=10)
            
            # Exemplo de recomendação
            if len(df) > 0:
                exemplo = df.iloc[0]['Nome']
                print(f"{'='*60}")
                print(f"EXEMPLO: Recomendações para '{exemplo}'")
                print(f"{'='*60}\n")
                
                recs = recomendar(exemplo, df, sim, top_n=5, incluir_score=True)
                
                if recs:
                    for i, (nome, score) in enumerate(recs, 1):
                        print(f"{i}. {nome}")
                        print(f"   Similaridade: {score:.3f} ({score*100:.1f}%)\n")
                else:
                    print("Nenhuma recomendação encontrada.")
                
                print(f"{'='*60}\n")
                
                # Demonstrar busca fuzzy
                print("Testando busca fuzzy (nome aproximado)...")
                # Pegar as 3 primeiras letras do primeiro jogo
                nome_parcial = exemplo[:3] if len(exemplo) >= 3 else exemplo
                try:
                    recs_fuzzy = recomendar(nome_parcial, df, sim, top_n=3)
                    print(f"Recomendações usando '{nome_parcial}': {recs_fuzzy}\n")
                except ValueError as e:
                    print(f"Erro: {e}\n")
                    
        except Exception as e:
            print(f"ERRO durante a execução: {e}")
            import traceback
            traceback.print_exc()
