# -*- coding: utf-8 -*-
"""
Módulo de Sistema de Recomendação pelo formulário
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from main import cadastro, clear

# ========== BASE DE DADOS DE JOGOS ==========
def criar_base_jogos():
    """Cria uma base de dados de jogos para o sistema de recomendação"""
    dados_jogos = {
        'Nome': [
            'The Witcher 3: Wild Hunt', 'Call of Duty: Warzone', 'FIFA 23', 'Minecraft', 'Grand Theft Auto V',
            'Counter-Strike 2', 'Red Dead Redemption 2', 'Fortnite', 'League of Legends', 'Valorant',
            'Cyberpunk 2077', 'Assassins Creed Valhalla', 'God of War', 'The Last of Us Part II', 'Halo Infinite',
            'Overwatch 2', 'Apex Legends', 'Rocket League', 'Among Us', 'Stardew Valley',
            'Elden Ring', 'Genshin Impact', 'Destiny 2', 'Terraria', 'Fall Guys',
            'Portal 2', 'The Legend of Zelda: Breath of the Wild', 'Dark Souls III', 'Resident Evil 4', 'Skyrim'
        ],
        'Gênero': [
            'RPG Ação', 'FPS Battle Royale', 'Esportes Futebol', 'Sandbox Sobrevivência', 'Ação Aventura',
            'FPS Tático', 'Ação Aventura', 'Battle Royale', 'MOBA', 'FPS Tático',
            'RPG Ação', 'Ação Aventura', 'Ação Aventura', 'Ação Aventura', 'FPS',
            'FPS Hero Shooter', 'Battle Royale FPS', 'Esportes Carros', 'Party Social', 'Simulação Fazenda',
            'RPG Ação', 'RPG Aventura', 'FPS RPG', 'Sandbox Aventura', 'Party Battle Royale',
            'Puzzle Aventura', 'Ação Aventura', 'RPG Ação', 'Survival Horror', 'RPG Aventura'
        ],
        'Plataforma': [
            'PC PlayStation Xbox', 'PC PlayStation Xbox', 'PC PlayStation Xbox', 'PC Mobile Console', 'PC PlayStation Xbox',
            'PC', 'PC PlayStation Xbox', 'PC PlayStation Xbox Mobile', 'PC', 'PC',
            'PC PlayStation Xbox', 'PC PlayStation Xbox', 'PlayStation', 'PlayStation', 'PC Xbox',
            'PC PlayStation Xbox', 'PC PlayStation Xbox', 'PC PlayStation Xbox', 'PC Mobile', 'PC Console Mobile',
            'PC PlayStation Xbox', 'PC PlayStation Mobile', 'PC PlayStation Xbox', 'PC Console Mobile', 'PC PlayStation',
            'PC Console', 'Nintendo Switch', 'PC PlayStation Xbox', 'PC PlayStation Xbox', 'PC PlayStation Xbox'
        ],
        'Modo de jogo': [
            'Single-player Mundo Aberto', 'Multiplayer Online', 'Multiplayer Online', 'Single-player Multiplayer', 'Single-player Multiplayer Mundo Aberto',
            'Multiplayer Online', 'Single-player Multiplayer Mundo Aberto', 'Multiplayer Online', 'Multiplayer Online', 'Multiplayer Online',
            'Single-player Mundo Aberto', 'Single-player Mundo Aberto', 'Single-player', 'Single-player', 'Multiplayer Online',
            'Multiplayer Online', 'Multiplayer Online', 'Multiplayer Online', 'Multiplayer Online', 'Single-player Multiplayer',
            'Single-player Multiplayer Mundo Aberto', 'Single-player Multiplayer', 'Multiplayer Online', 'Single-player Multiplayer', 'Multiplayer Online',
            'Single-player Cooperativo', 'Single-player Mundo Aberto', 'Single-player Multiplayer', 'Single-player', 'Single-player Mundo Aberto'
        ]
    }
    
    return pd.DataFrame(dados_jogos)

# ========== SISTEMA DE RECOMENDAÇÃO TF-IDF ==========
class SistemaRecomendacao:
    def __init__(self):
        self.df = criar_base_jogos()
        self.vectorizer = None
        self.tfidf_matrix = None
        self.similarity_matrix = None
        self._treinar_modelo()
    
    def _treinar_modelo(self):
        # Criar descrições concatenadas
        self.df['descricao'] = (
            self.df['Gênero'] + ' ' + 
            self.df['Plataforma'] + ' ' + 
            self.df['Modo de jogo']
        )
        
        # Aplicar TF-IDF
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
        """
        Gera recomendações baseadas no perfil do usuário
        
        Args:
            generos (list): Lista de gêneros preferidos
            plataformas (list): Lista de plataformas preferidas  
            modos_jogo (list): Lista de modos de jogo preferidos
            top_n (int): Número de recomendações a retornar
            
        Returns:
            list: Lista de dicionários com as recomendações
        """
        perfil_usuario = self.criar_perfil_usuario(generos, plataformas, modos_jogo)
        
        # Calcular similaridade entre perfil do usuário e todos os jogos
        similaridades = cosine_similarity(perfil_usuario, self.tfidf_matrix).flatten()
        
        # Obter índices dos jogos mais similares
        indices_similares = similaridades.argsort()[::-1]
        
        # Filtrar e ordenar recomendações
        recomendacoes = []
        for idx in indices_similares:
            if len(recomendacoes) >= top_n:
                break
            
            jogo = self.df.iloc[idx]
            score = similaridades[idx]
            
            # Adicionar à lista de recomendações
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

# ========== INTERFACE SIMPLIFICADA PARA O FRONTEND ==========
def inicializar_sistema():
    """
    Inicializa o sistema de recomendação
    Returns:
        SistemaRecomendacao: Instância do sistema
    """
    return SistemaRecomendacao()

def gerar_recomendacoes(sistema, preferencias_usuario, num_recomendacoes=10):
    """
    Função principal para o frontend chamar
    
    Args:
        sistema: Instância do SistemaRecomendacao
        preferencias_usuario (dict): Dicionário com preferências
            Exemplo: {
                'generos': ['Ação', 'RPG', 'Aventura'],
                'plataformas': ['PC', 'PlayStation'], 
                'modos_jogo': ['Single-player', 'Mundo Aberto']
            }
        num_recomendacoes (int): Número de recomendações
    
    Returns:
        dict: Resultado com recomendações e informações
    """
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

# ========== EXEMPLO PARA TESTE NO TERMINAL ==========
if __name__ == '__main__':
    # 1. Inicializar sistema
    print("🚀 Inicializando sistema de recomendação...")
    sistema_recomendacao = inicializar_sistema()
    info = sistema_recomendacao.get_info_sistema()
    print(f"✅ Sistema pronto! {info['total_jogos']} jogos carregados")
    
    # 2. CHAMAR O FORMULÁRIO DO MAIN.PY (para teste em terminal)
    print("\n📝 Iniciando formulário de preferências...")
    preferencias = cadastro()  # ← Isso chama SEU formulário original!
    
    # 3. Converter formato do formulário para o sistema
    generos, plataformas, modos_jogo = preferencias
    
    preferencias_para_sistema = {
        'generos': generos,
        'plataformas': plataformas, 
        'modos_jogo': modos_jogo
    }
    
    # 4. Gerar recomendações
    print("\n🎯 Gerando recomendações baseadas no seu perfil...")
    resultado = gerar_recomendacoes(sistema_recomendacao, preferencias_para_sistema, num_recomendacoes=10)
    
    # 5. Mostrar resultados
    if resultado['sucesso']:
        print(f"\n✅ {resultado['total_recomendacoes']} recomendações geradas:")
        for i, rec in enumerate(resultado['recomendacoes'], 1):
            print(f"\n{i}. {rec['nome']}")
            print(f"   Gênero: {rec['genero']}")
            print(f"   Plataforma: {rec['plataforma']}")
            print(f"   Modo: {rec['modo_jogo']}")
            print(f"   Similaridade: {rec['score_percentual']}")
    else:
        print(f"❌ Erro: {resultado['erro']}")