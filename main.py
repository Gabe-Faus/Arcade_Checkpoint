import os
import time
from colorama import Fore, Style, init
from recomendador_tfidf import *

init(autoreset=True)

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def formulario_generos(user):
    clear()
    print(Fore.BLUE + '\n' + ' Quais gêneros você gosta de jogar? '.center(90, '-'))

    Genres = {
        '1': 'Aventura', '2': 'Ação', '3': 'Metroidvania', '4': 'Puzzle', '5': 'Sandbox',
        '6': 'FPS', '7': 'Narrativo', '8': 'Simulação', '9': 'RPG',
        '10': 'Roguelike', '11': 'Horror', '12': 'Estratégia'
    }

    liked_genres = []

    while True:
        for nums, genres in Genres.items():
            print(f'\n\t|{nums:^3}|{genres:^15}|')

        liked_genres_id = input(Fore.BLUE + "\nDigite os números (mínimo 3), separados por espaço: ").split()

        if len(liked_genres_id) < 3:
            clear()
            print(Fore.RED + 'ATENÇÃO: Você precisa escolher ao menos 3 gêneros.\n')
            continue

        if not all(id_ in Genres for id_ in liked_genres_id):
            clear()
            print(Fore.RED + 'Erro: Você digitou um número que não existe. Tente novamente.\n')
            continue

        liked_genres = [Genres[id_] for id_ in liked_genres_id]
        break

    clear()
    return liked_genres


def formulario_plataformas(user):
    clear()
    print(Fore.BLUE + '\n' + ' Quais plataformas você geralmente usa? '.center(90, '-'))

    Platforms = {
        '1': 'PC', '2': 'PlayStation', '3': 'Xbox',
        '4': 'Multiplataforma', '5': 'Nintendo Switch', '6': 'Mobile'
    }

    liked_platforms = []

    while True:
        for nums, platforms in Platforms.items():
            print(f'\n\t|{nums:^3}|{platforms:^18}|')

        liked_platforms_id = input(Fore.BLUE + "\nDigite os números (mínimo 1), separados por espaço: ").split()

        if len(liked_platforms_id) < 1:
            clear()
            print(Fore.RED + 'ATENÇÃO: Você precisa selecionar ao menos 1 plataforma.\n')
            continue

        if not all(id_ in Platforms for id_ in liked_platforms_id):
            clear()
            print(Fore.RED + 'Erro: Você digitou um número que não existe. Tente novamente.\n')
            continue

        liked_platforms = [Platforms[id_] for id_ in liked_platforms_id]
        break

    clear()
    return liked_platforms


def formulario_modoJogo(user):
    clear()
    print(Fore.BLUE + '\n' + ' Quais são os seus modos de jogo favoritos? '.center(90, '-'))

    GameModes = {
        '1': 'Single-player',
        '2': 'Mundo Aberto',
        '3': 'Cooperativo',
        '4': 'Multiplayer online'
    }

    liked_GameModes = []

    while True:
        for nums, gameModes in GameModes.items():
            print(f'\n\t|{nums:^3}|{gameModes:^20}|')

        liked_GameModes_id = input(Fore.BLUE + "\nDigite os números (mínimo 2), separados por espaço: ").split()

        if len(liked_GameModes_id) < 2:
            clear()
            print(Fore.RED + 'ATENÇÃO: Você precisa selecionar ao menos 2 modos de jogo.\n')
            continue

        if not all(id_ in GameModes for id_ in liked_GameModes_id):
            clear()
            print(Fore.RED + 'Erro: Você digitou um número que não existe. Tente novamente.\n')
            continue

        liked_GameModes = [GameModes[id_] for id_ in liked_GameModes_id]
        break

    clear()
    return liked_GameModes


def cadastro():
    clear()
    print(Fore.BLUE + "*" * 90)
    print(Fore.BLUE + 'Bem-vindo ao Arcade Checkbox'.center(90))
    print(Fore.BLUE + "*" * 90)
    print(Fore.BLUE + '\nFaça seu cadastro:\n'.center(90))

    user = input(Fore.BLUE + '\tDigite seu nome: ')
    password = input(Fore.BLUE + '\tDigite sua senha: ')

    clear()

    print(Fore.BLUE + f'{user}, agora vamos fazer um questionário para saber o seu perfil de jogador.\n')
    print(Fore.BLUE + 'É importante que você responda com pelo menos:')
    print(Fore.BLUE + '- 3 gêneros\n- 1 plataforma\n- 2 modos de jogo\n')

    input(Fore.BLUE + "\nPressione ENTER para continuar...")
    clear()

    generos = formulario_generos(user)
    plataformas = formulario_plataformas(user)
    modosJogo = formulario_modoJogo(user)

    preferencias = [generos, plataformas, modosJogo]

    print(Fore.BLUE + f'\n{user}, este é o resumo das suas preferências:\n'.center(90))
    for perfs in preferencias:
        print(Fore.BLUE + f"{', '.join(perfs)}".center(90))
    print()

    return preferencias


if __name__ == '__main__':
    print("🚀 Inicializando sistema de recomendação...")
    sistema_recomendacao = inicializar_sistema()
    info = sistema_recomendacao.get_info_sistema()
    print(f"O Sistema está pronto! {info['total_jogos']} jogos carregados")
    
    print("\nIniciando formulário de preferências...")
    preferencias = cadastro()  
    
    generos, plataformas, modos_jogo = preferencias
    
    preferencias_para_sistema = {
        'generos': generos,
        'plataformas': plataformas, 
        'modos_jogo': modos_jogo
    }
    

    print(Fore.BLUE + f'\nGerando recomendações baseadas no teu perfil...')
    resultado = gerar_recomendacoes(sistema_recomendacao, preferencias_para_sistema, num_recomendacoes=10)
    

    if resultado['sucesso']:
        print(Fore.BLUE + f"\n{resultado['total_recomendacoes']} recomendações geradas:")
        for i, rec in enumerate(resultado['recomendacoes'], 1):
            print(Fore.BLUE + f"\n{i}. {rec['nome']}")
            print(Fore.GREEN + f"   Gênero: {rec['genero']}")
            print(Fore.GREEN + f"   Plataforma: {rec['plataforma']}")
            print(Fore.GREEN + f"   Modo: {rec['modo_jogo']}")
            print(Fore.GREEN + f"   Similaridade: {rec['score_percentual']}")
    else:
        print(Fore.RED + f"Erro: {resultado['erro']}")
