# -*- coding: utf-8 -*-
"""
Módulo de Sistema de Recomendação pelo formulário
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from main import cadastro, clear

def criar_base_jogos():

    df = pd.read_csv("C:\\Users\\faust\\Desktop\\Sistema de Recomendação\\fontes\\jogos_carac.csv", encoding="utf-8")

    for col in ["Nome", "Gênero", "Plataforma", "Modo de jogo"]:
        df[col] = df[col].astype(str).str.strip()

    return df

class SistemaRecomendacao:
    def __init__(self):
        self.df = criar_base_jogos()
        self.vectorizer = None
        self.tfidf_matrix = None
        self.similarity_matrix = None
        self._treinar_modelo()
    
    def _treinar_modelo(self):
        self.df['descricao'] = (
            self.df['Gênero'] + ' ' + 
            self.df['Plataforma'] + ' ' + 
            self.df['Modo de jogo']
        )
        
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.95
        )
        
        self.tfidf_matrix = self.vectorizer.fit_transform(self.df['descricao'])
        self.similarity_matrix = cosine_similarity(self.tfidf_matrix)
    
    def criar_perfil_usuario(self, generos, plataformas, modos_jogo):
        """Cria um perfil TF-IDF baseado nas preferências do usuário"""
        perfil_texto = ' '.join(generos) + ' ' + ' '.join(plataformas) + ' ' + ' '.join(modos_jogo)
        perfil_tfidf = self.vectorizer.transform([perfil_texto])
        return perfil_tfidf
    
    def recomendar(self, generos, plataformas, modos_jogo, top_n=10):
    
        perfil_usuario = self.criar_perfil_usuario(generos, plataformas, modos_jogo)
        
        similaridades = cosine_similarity(perfil_usuario, self.tfidf_matrix).flatten()
        
        indices_similares = similaridades.argsort()[::-1]

        recomendacoes = []
        for idx in indices_similares:
            if len(recomendacoes) >= top_n:
                break
            
            jogo = self.df.iloc[idx]
            score = similaridades[idx]
   
            recomendacoes.append({
                'nome': jogo['Nome'],
                'genero': jogo['Gênero'],
                'plataforma': jogo['Plataforma'],
                'modo_jogo': jogo['Modo de jogo'],
                'score_similaridade': float(score),
                'score_percentual': f"{score*100:.1f}%"
            })
        
        return recomendacoes

    def get_info_sistema(self):
        """Retorna informações sobre o sistema"""
        return {
            'total_jogos': len(self.df),
            'tamanho_vocabulario': len(self.vectorizer.get_feature_names_out()),
            'forma_matriz_tfidf': self.tfidf_matrix.shape
        }


def inicializar_sistema():
    return SistemaRecomendacao()

def gerar_recomendacoes(sistema, preferencias_usuario, num_recomendacoes=10):
   
    try:
        recomendacoes = sistema.recomendar(
            generos=preferencias_usuario['generos'],
            plataformas=preferencias_usuario['plataformas'],
            modos_jogo=preferencias_usuario['modos_jogo'],
            top_n=num_recomendacoes
        )
        
        return {
            'sucesso': True,
            'recomendacoes': recomendacoes,
            'total_recomendacoes': len(recomendacoes),
            'info_sistema': sistema.get_info_sistema()
        }
        
    except Exception as e:
        return {
            'sucesso': False,
            'erro': str(e),
            'recomendacoes': [],
            'total_recomendacoes': 0
        }
