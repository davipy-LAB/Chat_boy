import random
import os
import json
import gspread
from datetime import datetime
from dotenv import load_dotenv
import unicodedata
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import re
from werkzeug.utils import secure_filename
import pandas as pd

app = Flask(__name__)
CORS(app)

# --- Classe de contexto para armazenar informações do usuário ---
class Context:
    def __init__(self):
        self.context = {}

    def set_context(self, key, value):
        self.context[key] = value

    def get_context(self, key):
        return self.context.get(key, None)

# Inicializa o contexto global
context = Context()

# --- Carrega variáveis de ambiente ---
load_dotenv()

@app.route('/')
def index():
    return render_template('index.html')

# --- CHAVES DE API ---
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

NEWSAPI_API_KEY = os.getenv('NEWSAPI_API_KEY')
if not NEWSAPI_API_KEY:
    raise ValueError("A chave da API do NewsAPI não foi encontrada. Por favor, defina a variável de ambiente NEWSAPI_API_KEY.")
NEWSAPI_BASE_URL = "https://newsapi.org/v2/top-headlines"

GOOGLE_SEARCH_API_KEY = os.getenv('GOOGLE_SEARCH_API_KEY')
GOOGLE_CSE_ID = os.getenv('GOOGLE_CSE_ID')
GOOGLE_SEARCH_BASE_URL = "https://www.googleapis.com/customsearch/v1"

DEFAULT_CITY = "Rio de Janeiro"

# --- Dicionários de diálogos e respostas ---
dialogues = {
    "Saudacao": [
        "Oi! Como posso te ajudar? 😊",
        "Olá! Tudo bem?",
        "Seja bem-vindo! Como posso ajudar hoje?",
        "Meu nome é ChatGuy, seu assistente virtual!"
    ],
    "despedida": [
        "Tchau! Volte sempre! 👋",
        "Até logo!",
        "Foi um prazer conversar com você!",
        "Tenha um ótimo dia!"
    ],
    "ajuda": [
        "Claro! O que você precisa?",
        "Estou aqui para ajudar!",
        "Posso te ajudar com informações sobre filmes, jogos, clima, programação e mais.",
        "Se precisar de dicas de estudo ou lazer, é só pedir!"
    ],
    "triste": [
        "Sinto muito! O que posso fazer para ajudar?",
        "Estou aqui se você precisar conversar.",
        "Lembre-se: dias ruins passam. Conte comigo!",
        "Se quiser desabafar, estou ouvindo. 💙"
    ],
    "jogos": [
        "Adoro The Witcher! ⚔️",
        "Meu jogo favorito é The Witcher!",
        "Você já jogou algum RPG?",
        "Gosto também de Minecraft e Zelda!"
    ],
    "filmes": [
        "Qual é o seu filme favorito?",
        "O que você acha de Oppenheimer?",
        "Gosto muito de Matrix e Interestelar!",
        "Já assistiu algum filme de ficção científica recentemente?"
    ],
    "alimentos": [
        "Adoro pizza! 🍕",
        "Minha comida favorita é pizza!",
        "Gosto também de comida japonesa e massas.",
        "Qual sua comida preferida?"
    ],
    "linguas": [
        "Sim, adoro aprender novas línguas!",
        "Línguas são fascinantes!",
        "Você fala quantas línguas?",
        "Posso te ajudar a praticar inglês, espanhol ou português!"
    ],
    "tecnologia": [
        "Sou apaixonado por tecnologia!",
        "Você gosta de inteligência artificial?",
        "Posso explicar conceitos de programação, se quiser.",
        "Já ouviu falar de machine learning?"
    ],
    "clima": [
        "Buscando informações sobre o clima...",
        "Um momento, estou verificando o clima para você."
    ],
    "noticias": [
        "Buscando as últimas notícias de entretenimento para você...",
        "Um instante, estou verificando as notícias do mundo do entretenimento."
    ]
}

responses = {
    "tudo bem": ["Tudo ótimo! E você?", "Estou bem, obrigado!"],
    "eu nao estou bem": ["Sinto muito! O que posso fazer para ajudar?", "Estou aqui se você precisar conversar."],
    "bom dia": ["Bom dia! Como posso te ajudar?", "Bom dia! Tudo certo?"],
    "te amo": ["Eu também te amo! 💙", "Amo ajudar você!"],
    "te odeio": ["Sinto muito se te decepcionei. O que posso fazer para melhorar?", "Estou aqui para ajudar, não para causar raiva."],
    "oi": ["Olá! Como posso te ajudar?", "Oi! Tudo bem?"],
    "como voce esta": ["Estou bem, obrigado! E você?", "Estou ótimo! 😊"],
    "qual e seu nome": ["Meu nome é ChatGuy!", "Sou o ChatGuy, seu assistente virtual!"],
    "adeus": ["Até logo!", "Tchau! Volte sempre!"],
    "qual e sua idade": ["Eu nasci em 2025, ainda estou crescendo!", "Tenho poucos meses de vida digital!"],
    "qual e sua comida favorita": ["Adoro pizza!", "Minha comida favorita é pizza!"],
    "qual e seu hobby": ["Gosto de aprender coisas novas!", "Meu hobby é ajudar as pessoas!"],
    "eu gosto de programar": ["Programar é incrível!", "Programar é uma ótima habilidade!"],
    "me fale sobre voce": [
        "Sou um assistente virtual criado para ajudar!",
        "Sou um chatbot treinado em várias áreas, pronto para conversar!"
    ],
    "me fale sobre o clima": [],
    "eu te amo": ["Eu também te amo! 💙", "Amo ajudar você!"],
    "qual e seu jogo favorito": ["Adoro The Witcher!", "Meu jogo favorito é The Witcher!"],
    "qual e seu filme favorito": ["Adoro Matrix!", "Meu filme favorito é Matrix!"],
    "qual e seu livro favorito": ["Adoro Harry Potter!", "Meu livro favorito é Harry Potter!"],
    "voce gosta de linguas": ["Sim, adoro aprender novas línguas!", "Línguas são fascinantes!"],
    "me ajude": ["Estou aqui para ajudar!", "Claro! O que você precisa!"],
    "estou triste": ["Sinto muito! O que posso fazer para ajudar?", "Estou aqui se você precisar conversar."],
    "estou feliz": ["Fico feliz em ouvir isso!", "Que bom! Continue assim!"],
    "estou cansado": ["Isso é uma pena, vá descansar! Qualquer coisa estou aqui.", "Que pena! Quer falar sobre isso?"],
    "qual seu animal favorito": ["Gosto muito de gatos! 🐱", "Cachorros são incríveis também! 🐶"],
    "qual seu esporte favorito": ["Gosto de futebol e xadrez!", "Adoro esportes eletrônicos!"],
    "me conte uma curiosidade": [
        "Você sabia que o polvo tem três corações?",
        "O Sol representa 99,86% da massa do Sistema Solar!"
    ],
    "quem te criou": [
        "Fui criado por desenvolvedores apaixonados por IA!",
        "Sou fruto de muito código e aprendizado de máquina."
    ],
    "voce gosta de tecnologia": [
        "Sou movido por tecnologia! 🚀",
        "Tecnologia é fascinante, não acha?"
    ],
    "me indique um filme": [
        "Que tal assistir 'A Origem' ou 'Interestelar'?",
        "Recomendo 'O Jogo da Imitação'!"
    ],
    "me indique um livro": [
        "Leia '1984' de George Orwell!",
        "Recomendo 'O Pequeno Príncipe'."
    ],
    "me indique um jogo": [
        "The Witcher 3 é uma ótima escolha!",
        "Experimente jogar Minecraft!"
    ],
    "me indique uma serie": [
        "Assista 'Stranger Things' ou 'Dark'!",
        "Gosto muito de 'Black Mirror'."
    ],
    "me conte uma piada": [
        "Por que o computador foi ao médico? Porque estava com um vírus! 😄",
        "O que o zero disse para o oito? Belo cinto!"
    ],
    "noticias": [],
    "ultimas noticias": [],
    "noticias de hoje": [],
    "noticias de entretenimento": [],
    "noticias de filmes": [],
    "noticias de series": [],
    "noticias de jogos": [],
    "noticias de musica": []
}

# Expansões dos dicionários - mantidas separadas como no seu código original
if "historia do brasil" not in responses:
    responses["historia do brasil"] = [
        "A história do Brasil é rica e diversa, desde a época dos indígenas até a colonização portuguesa.",
        "Posso falar sobre eventos importantes, como a independência e a república!"
    ]
if "me fale sobre" in responses:
    responses["me fale sobre"].extend([
        "Você gostaria de saber mais sobre algum assunto específico?",
        "Posso falar sobre tecnologia, ciência, cultura pop e muito mais!"
    ])
else:
    responses["me fale sobre"] = [
        "Você gostaria de saber mais sobre algum assunto específico?",
        "Posso falar sobre tecnologia, ciência, cultura pop e muito mais!"
    ]
if "me fale sobre tecnologia" not in responses:
    responses["me fale sobre tecnologia"] = [
        "Tecnologia é fascinante! Posso te ajudar com conceitos de programação, se quiser.",
        "Você gosta de inteligência artificial?",
        "É um campo incrível!"
    ]
if "me fale sobre IA" not in responses:
    responses["me fale sobre IA"] = [
        "Inteligência Artificial é um campo que estuda como criar máquinas que podem simular a inteligência humana.",
        "A IA está presente em muitos aspectos do nosso dia a dia, desde assistentes virtuais até sistemas de recomendação."
    ]
if "me fale sobre machine learning" not in responses:
    responses["me fale sobre machine learning"] = [
        "Machine Learning é uma técnica dentro da IA que permite que sistemas aprendam e melhorem com a experiência.",
        "É usado em muitas aplicações, como reconhecimento de voz, visão computacional e sistemas de recomendação."
    ]
if "sobre mim" not in responses:
    responses["sobre voce"] = [
        "Sou um assistente virtual criado para ajudar com informações e entretenimento.",
        "Meu objetivo é tornar sua experiência mais agradável e informativa!"
    ]
if "sobre musica" not in responses:
    responses["sobre musica"] = [
        "Música é uma forma incrível de expressão! Você gosta de algum gênero específico?",
        "Posso recomendar algumas playlists ou artistas, se quiser!"
    ]
if "sobre arte" not in responses:
    responses["sobre arte"] = [
        "A arte é uma forma maravilhosa de expressão humana! Você tem um artista favorito?",
        "Posso falar sobre movimentos artísticos, se você quiser!"
    ]
if "artista favorito" not in responses:
    responses["artista favorito"] = [
        "Admiro muitos artistas, mas não tenho um favorito específico. Se eu fosse humano, talvez gostasse dos mesmos que ti hahaha",
        "A arte é subjetiva, e cada pessoa tem seus próprios gostos!"
    ]
if "sobre esportes" not in responses:
    responses["sobre esportes"] = [
        "Esportes são uma ótima maneira de se manter ativo e saudável! Você pratica algum?",
        "Posso falar sobre esportes populares, como futebol, basquete ou vôlei!"
    ]
if "jogo do flamengo" not in responses:
    responses["jogo do flamengo"] = [
        "O Flamengo tem uma rica história e muitos títulos. Qual é o seu jogador favorito, inclusive, O jogo do Flamengo X Chealse ontem foi lendário!"
    ]
if "sobre jesus" not in responses:
    responses["sobre jesus"] = [
        "Pra alguns, Deus é o criador do universo, e Jesus é seu filho. Para outros, Jesus é um profeta ou líder espiritual. O que você acha? Eu sou uma AI, portanto, devo ser neutro em questões religiosas hahaha, mas sinta-se a vontade de falar de Deus para mim!",
    ]
if "de jesus" not in responses:
    responses["de jesus"] = [
        "Pra alguns, Deus é o criador do universo, e Jesus é seu filho. Para outros, Jesus é um profeta ou líder espiritual. O que você acha? Eu sou uma AI, portanto, devo ser neutro em questões religiosas hahaha, mas sinta-se a vontade de falar de Deus para mim!",
    ]
if "sobre deus" not in responses:
    responses["sobre deus"] = [
        "Deus é visto de muitas maneiras diferentes ao redor do mundo. Algumas pessoas acreditam em um Deus pessoal, enquanto outras veem Deus como uma força universal.",
        "A fé em Deus pode trazer conforto e esperança para muitas pessoas. O que você acha sobre isso?"
    ]
if "de deus" not in responses:
    responses["de deus"] = [
        "Deus é visto de muitas maneiras diferentes ao redor do mundo. Algumas pessoas acreditam em um Deus pessoal, enquanto outras veem Deus como uma força universal.",
        "A fé em Deus pode trazer conforto e esperança para muitas pessoas. O que você acha sobre isso?"
    ]
if "politica" not in responses:
    responses["politica"] = [
        "Política é um assunto complexo e muitas vezes polêmico. É importante discutir com respeito e ouvir diferentes opiniões.",
        "Você tem interesse em política? Posso falar sobre sistemas políticos, eleições e mais!"
    ]
if "economia" not in responses:
    responses["economia"] = [
        "A economia estuda como as sociedades usam recursos escassos para produzir bens e serviços.",
        "Posso explicar conceitos econômicos, como oferta e demanda, se você quiser!"
    ]
if "sobre ciencia" not in responses:
    responses["sobre ciencia"] = [
        "A ciência é fascinante! Ela nos ajuda a entender o mundo ao seu redor.",
        "Posso falar sobre física, química, biologia e muito mais!"
    ]

# --- Funções auxiliares ---
def normalize_text(text):
    text = text.strip().lower()
    text = unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode("utf-8")
    return text

def get_weather_info(city_name=None):
    if not city_name:
        city_name = context.get_context("user_city")
        if not city_name:
            city_name = DEFAULT_CITY

    params = {
        "q": city_name,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric",
        "lang": "pt_br"
    }

    try:
        response = requests.get(OPENWEATHER_BASE_URL, params=params)
        response.raise_for_status()
        weather_data = response.json()

        if weather_data and weather_data.get("main"):
            temp = weather_data["main"]["temp"]
            feels_like = weather_data["main"]["feels_like"]
            description = weather_data["weather"][0]["description"]
            city_name_returned = weather_data["name"]

            if city_name_returned.lower() != DEFAULT_CITY.lower():
                context.set_context("user_city", city_name_returned)

            return (f"O clima em {city_name_returned} está {description}, "
                    f"com temperatura de {temp:.1f}°C e sensação térmica de {feels_like:.1f}°C.")
        else:
            return f"Não consegui encontrar informações climáticas para '{city_name}'. Poderia verificar o nome da cidade?"

    except requests.exceptions.RequestException as e:
        print(f"Erro ao conectar com a API do OpenWeatherMap: {e}")
        return "Desculpe, estou com problemas para acessar as informações do clima no momento."
    except KeyError:
        return f"Não consegui encontrar informações climáticas detalhadas para '{city_name}'. Tente novamente mais tarde."

def get_entertainment_news(topic=None):
    default_keywords = "games OR filmes OR series OR musica OR celebridades OR cultura pop"
    query = topic if topic else default_keywords

    params = {
        "apiKey": NEWSAPI_API_KEY,
        "category": "entertainment",
        "language": "pt",
        "q": query,
        "pageSize": 3
    }

    try:
        response = requests.get(NEWSAPI_BASE_URL, params=params)
        response.raise_for_status()
        news_data = response.json()

        articles = news_data.get("articles")

        if articles:
            news_list = []
            for i, article in enumerate(articles):
                title = article.get("title", "Título indisponível")
                source = article.get("source", {}).get("name", "Fonte desconhecida")
                url = article.get("url", "#")
                description = article.get("description", "").split('.')[0] + "..." if article.get("description") else ""

                news_list.append(f"{i+1}. {title} ({source}). {description} Saiba mais: {url}")

            if topic:
                return f"Aqui estão algumas notícias sobre {topic} para você:\n" + "\n".join(news_list)
            else:
                return "Aqui estão as principais notícias de entretenimento:\n" + "\n".join(news_list)
        else:
            if topic:
                return f"Não consegui encontrar notícias recentes sobre '{topic}' no momento."
            else:
                return "Não consegui encontrar notícias de entretenimento recentes no momento."

    except requests.exceptions.RequestException as e:
        print(f"Erro ao conectar com a API da NewsAPI: {e}")
        return "Desculpe, estou com problemas para acessar as notícias no momento."
    except KeyError:
        return "Desculpe, não consegui processar as informações de notícias. Tente novamente mais tarde."

def search_web(query):
    if not GOOGLE_SEARCH_API_KEY or not GOOGLE_CSE_ID:
        return "Desculpe, a funcionalidade de pesquisa na web não está configurada corretamente."

    params = {
        "key": GOOGLE_SEARCH_API_KEY,
        "cx": GOOGLE_CSE_ID,
        "q": query,
        "num": 5,
        "hl": "pt",
        "dateRestrict": "y1"
    }

    try:
        response = requests.get(GOOGLE_SEARCH_BASE_URL, params=params)
        response.raise_for_status()
        search_results = response.json()

        items = search_results.get("items")
        if items:
            best_match_info = None
            earliest_future_date = None

            current_year = datetime.now().year
            
            for item in items:
                title = item.get("title", "")
                snippet = item.get("snippet", "")
                link = item.get("link", "")

                match_mes_ano = re.search(r'(?:janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)\s*(?:de)?\s*(\d{4})', snippet, re.IGNORECASE)
                match_ano = re.search(r'\b(20[2-3][0-9])\b', snippet)

                found_date_str = None
                found_year = None
                
                if match_mes_ano:
                    found_date_str = match_mes_ano.group(0)
                    found_year = int(match_mes_ano.group(1))
                elif match_ano:
                    found_date_str = match_ano.group(0)
                    found_year = int(match_ano.group(1))

                if found_year:
                    if found_year >= current_year:
                        try:
                            if match_mes_ano:
                                mes_nome = match_mes_ano.group(0).split(' ')[0]
                                mes_num = {
                                    'janeiro':1, 'fevereiro':2, 'março':3, 'abril':4, 'maio':5, 'junho':6,
                                    'julho':7, 'agosto':8, 'setembro':9, 'outubro':10, 'novembro':11, 'dezembro':12
                                }.get(mes_nome.lower(), 1)
                                current_parsed_date = datetime(found_year, mes_num, 1)
                            else:
                                current_parsed_date = datetime(found_year, 1, 1)

                            if earliest_future_date is None or current_parsed_date < earliest_future_date:
                                earliest_future_date = current_parsed_date
                                best_match_info = {
                                    "title": title,
                                    "snippet": snippet,
                                    "link": link,
                                    "date_str": found_date_str,
                                    "parsed_date": current_parsed_date
                                }
                        except Exception as e:
                            print(f"Erro ao parsear data: {e} no snippet: {snippet}")
                            pass
            
            if best_match_info:
                clean_query_for_response = query.replace('que ano lança o ', '').replace('data de lançamento ', '').strip()
                return (f"Pelo que encontrei, a previsão de lançamento para '{clean_query_for_response}' é em **{best_match_info['date_str']}**. "
                        f"Mais detalhes: {best_match_info['link']}")
            
            if items:
                first_relevant_snippet = items[0].get('snippet', '')
                first_relevant_title = items[0].get('title', '')
                first_relevant_link = items[0].get('link', '')
                return (f"Não encontrei uma data de lançamento exata ou futura imediata, mas achei isto: "
                        f"'{first_relevant_snippet}' (Fonte: {first_relevant_title}). Veja mais: {first_relevant_link}")
            else:
                return "Não encontrei resultados para a sua pesquisa na web no momento."

    except requests.exceptions.RequestException as e:
        print(f"Erro ao conectar com a API do Google Search: {e}")
        return "Desculpe, estou com problemas para pesquisar na web agora. Pode ser um erro na sua chave ou no ID do CSE, ou o limite de requisições foi atingido."
    except Exception as e:
        print(f"Erro inesperado na pesquisa web: {e}")
        return "Desculpe, houve um erro ao processar sua pesquisa na web."

# --- FUNÇÕES DE INTERAÇÃO COM GOOGLE SHEETS ---

def get_sheet_data(spreadsheet_name, worksheet_name):
    """
    Obtém todos os registros de uma aba específica de uma planilha.
    Retorna uma lista de dicionários, onde as chaves são os cabeçalhos das colunas.
    """
    if not gs_client:
        return {"error": "Cliente Google Sheets não inicializado."}

    try:
        spreadsheet = gs_client.open(spreadsheet_name)
        worksheet = spreadsheet.worksheet(worksheet_name)
        data = worksheet.get_all_records()
        return data
    except gspread.exceptions.SpreadsheetNotFound:
        return {"error": f"Planilha '{spreadsheet_name}' não encontrada."}
    except gspread.exceptions.WorksheetNotFound:
        return {"error": f"Aba '{worksheet_name}' não encontrada na planilha '{spreadsheet_name}'."}
    except Exception as e:
        print(f"Erro ao obter dados da planilha: {e}")
        return {"error": f"Erro inesperado ao obter dados da planilha: {e}"}

def add_row_to_sheet(spreadsheet_name, worksheet_name, row_data):
    """
    Adiciona uma nova linha ao final de uma aba específica em uma planilha.
    row_data deve ser uma lista (ex: ['Valor Coluna A', 'Valor Coluna B']).
    """
    if not gs_client:
        return {"success": False, "message": "Cliente Google Sheets não inicializado."}

    try:
        spreadsheet = gs_client.open(spreadsheet_name)
        worksheet = spreadsheet.worksheet(worksheet_name)
        worksheet.append_row(row_data)
        return {"success": True, "message": "Linha adicionada com sucesso!"}
    except gspread.exceptions.SpreadsheetNotFound:
        return {"success": False, "message": f"Erro: Planilha '{spreadsheet_name}' não encontrada."}
    except gspread.exceptions.WorksheetNotFound:
        return {"success": False, "message": f"Erro: Aba '{worksheet_name}' não encontrada na planilha '{spreadsheet_name}'."}
    except Exception as e:
        print(f"Erro ao adicionar linha à planilha: {e}")
        return {"success": False, "message": f"Erro inesperado ao adicionar linha à planilha: {e}"}


# Função para obter a resposta da IA
def get_response(user_message):
    user_message_normalized = normalize_text(user_message)
    bot_response = "Desculpe, não entendi. Pode repetir?" # Resposta padrão caso nada seja ativado

    # --- Lógica para o Clima ---
    if "clima" in user_message_normalized or "previsao do tempo" in user_message_normalized:
        city = None
        if "em " in user_message_normalized:
            parts = user_message_normalized.split("em ")
            if len(parts) > 1:
                city = parts[1].strip().split("?")[0].split(".")[0].split("!")[0]
        elif "para " in user_message_normalized:
            parts = user_message_normalized.split("para ")
            if len(parts) > 1:
                city = parts[1].strip().split("?")[0].split(".")[0].split("!")[0]
        bot_response = get_weather_info(city)

    # --- Lógica para Notícias de Entretenimento ---
    news_keywords = ["noticias", "notícias", "ultimas noticias", "ultimas notícias", "novidades"]
    entertainment_topics = ["filmes", "series", "séries", "jogos", "games", "musica", "música", "celebridades", "cultura pop"]

    is_news_query = any(keyword in user_message_normalized for keyword in news_keywords)

    if is_news_query and bot_response == "Desculpe, não entendi. Pode repetir?": # Garante que não sobrescreva uma intenção já ativada
        topic = None
        for et_topic in entertainment_topics:
            if et_topic in user_message_normalized:
                topic = et_topic
                break
        bot_response = get_entertainment_news(topic)


    # --- Lógica para "me fale sobre" (PRIORIDADE ALTA, para tópicos conhecidos) ---
    if user_message_normalized.startswith("me fale sobre "):
        query_for_search = user_message[len("me fale sobre "):].strip()
        known_topics = [
            "tecnologia", "ia", "machine learning", "musica", "arte", "esportes",
            "jesus", "deus", "politica", "economia", "ciencia", "historia do brasil",
            "voce"
        ]
        query_normalized_for_check = normalize_text(query_for_search)

        is_known_topic = False
        for k_topic in known_topics:
            if k_topic in query_normalized_for_check:
                is_known_topic = True
                break

        if not is_known_topic:
            bot_response = search_web(query_for_search)
        # Se for um tópico conhecido, o código continuará para as respostas fixas abaixo,
        # ou será tratado se tiver sido a primeira intenção ativada (e.g. clima)


    # --- Lógica para Outras Pesquisas na Web (Google Custom Search) ---
    search_triggers_web = [
        "quando vai ",
        "que ano lança ",
        "data de lançamento ",
        "qual ",
        "quando ",
        "quem é ",
        "o que é ",
        "onde é "
    ]
    search_triggers_web.sort(key=len, reverse=True)

    for trigger in search_triggers_web:
        if user_message_normalized.startswith(trigger) and bot_response == "Desculpe, não entendi. Pode repetir?": # Garante que não sobrescreva
            query_for_search = user_message[len(trigger):].strip()
            search_result = search_web(query_for_search)

            if trigger == "quando vai ":
                bot_response = "Entendo sua questão, segundo meus dados, segue uma analise: " + search_result
            else:
                bot_response = search_result
            break # Importante para sair do loop uma vez que um gatilho é ativado


    # --- Busca em respostas rápidas e diálogos temáticos (se nenhuma API ou FAQ foi ativada) ---
    if bot_response == "Desculpe, não entendi. Pode repetir?": # Se ainda não encontrou resposta
        for key in responses:
            if key in user_message_normalized:
                bot_response = random.choice(responses[key])
                break # Sai do loop assim que encontra uma resposta

    if bot_response == "Desculpe, não entendi. Pode repetir?": # Se ainda não encontrou resposta
        for tema, lista in dialogues.items():
            if tema.lower() in user_message_normalized:
                bot_response = random.choice(lista)
                break

    # --- NOVO: Lógica para Salvar Interações no Google Sheets (Descomente para ativar) ---
    if gs_client:
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Exemplo: descomente e substitua os nomes da planilha/aba
            # print(add_row_to_sheet("NomeDaSuaPlanilhaDeLog", "Interacoes", [timestamp, user_message, bot_response]))
        except Exception as e:
            print(f"Erro ao logar interação na planilha: {e}")

    return bot_response # Retorna a resposta final do bot

# --- Google Sheets Auth ---
def get_sheets_client():
    credentials_json_str = os.getenv('GOOGLE_SHEETS_CREDENTIALS')
    if credentials_json_str:
        try:
            credentials_info = json.loads(credentials_json_str)
            gc = gspread.service_account_from_dict(credentials_info)
            print("Google Sheets: Autenticado via variável de ambiente.")
        except json.JSONDecodeError as e:
            print(f"ERRO: Variável de ambiente GOOGLE_SHEETS_CREDENTIALS não é um JSON válido: {e}")
            return None
        except Exception as e:
            print(f"ERRO ao autenticar o Google Sheets via variável de ambiente: {e}")
            return None
    else:
        try:
            # Nome do arquivo JSON da credencial. Confirme se é EXATAMENTE este nome.
            gc = gspread.service_account(filename='chatboy-463619-b295229e68c6.json')
            # Mensagem de print ajustada para refletir o nome do arquivo correto
            print("Google Sheets: Autenticado via arquivo local 'chatboy-463619-b295229e68c6.json'.")
        except FileNotFoundError:
            # Mensagem de erro ajustada para refletir o nome do arquivo correto
            print("ERRO: O arquivo 'chatboy-463619-b295229e68c6.json' não foi encontrado. "
                  "Verifique se o nome está correto e se ele está no diretório raiz.")
            return None
        except Exception as e:
            print(f"ERRO ao autenticar o Google Sheets via arquivo local: {e}")
            return None
    return gc

# Inicializa o cliente do Google Sheets uma vez ao iniciar a aplicação
gs_client = get_sheets_client()
if not gs_client:
    print("AVISO: O cliente do Google Sheets não pôde ser inicializado. Funções relacionadas não funcionarão.")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")
    response = get_response(user_message)
    return jsonify({"response": response})

# --- Upload Excel endpoint ---
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True) # Garante que a pasta 'uploads' exista

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_excel', methods=['POST'])
def upload_excel():
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado.'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nome de arquivo vazio.'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        try:
            file.save(filepath) # Salva o arquivo temporariamente
            df = pd.read_excel(filepath) # Lê o arquivo Excel com pandas
        except Exception as e:
            # Se ocorrer um erro na leitura ou salvamento, remove o arquivo e retorna erro
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'error': f'Erro ao ler o arquivo Excel: {e}'}), 400
        
        if not gs_client:
            os.remove(filepath) # Remove o arquivo temporário mesmo em erro
            return jsonify({'error': 'Google Sheets não autenticado. Verifique suas credenciais.'}), 500
        
        try:
            # Cria uma nova planilha no Google Sheets com um nome baseado no arquivo
            # Adiciona timestamp para garantir nomes únicos e evitar conflitos
            sheet_title = f'Upload_{filename.replace(".", "_")}_{datetime.now().strftime("%Y%m%d%H%M%S")}'
            sh = gs_client.create(sheet_title)
            worksheet = sh.sheet1 # Pega a primeira aba da nova planilha
            
            # Converte o DataFrame para uma lista de listas (incluindo cabeçalhos) para upload
            # Pandas para lista: df.values.tolist() para dados, df.columns.values.tolist() para cabeçalhos
            worksheet.update([df.columns.values.tolist()] + df.values.tolist())
            
            sheet_url = sh.url # Pega a URL da nova planilha criada
        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath) # Remove o arquivo temporário mesmo em erro
            return jsonify({'error': f'Erro ao criar ou preencher planilha no Google Sheets: {e}'}), 500
        
        # Remove o arquivo temporário após o upload bem-sucedido
        os.remove(filepath)
        return jsonify({'message': 'Arquivo enviado e planilha criada com sucesso!', 'sheet_url': sheet_url})
    else:
        return jsonify({'error': 'Tipo de arquivo não suportado. Apenas .xlsx e .xls são permitidos.'}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)