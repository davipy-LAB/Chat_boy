import random
import os
import json
# from urllib import response # Este import não é necessário e pode ser removido
import gspread
from datetime import datetime
from dotenv import load_dotenv
import unicodedata
# Adicione/Mantenha todos os imports do Flask aqui, incluindo 'session', 'url_for', 'g'
from flask import Flask, request, jsonify, render_template, session, url_for, g, redirect
from flask_cors import CORS
import requests
import re
from google.oauth2.service_account import Credentials
from werkzeug.utils import secure_filename
import pandas as pd
import pytz
import psycopg2
import sys
from werkzeug.security import generate_password_hash, check_password_hash # Adicione estes aqui também

# --- Inicialização do Flask App ---
app = Flask(__name__)
CORS(app) # Se você estiver usando CORS

# --- Carrega variáveis de ambiente (DEVE SER CHAMADO ANTES DE ACESSAR OS.GETENV) ---
load_dotenv()

# --- CHAVE SECRETA PARA SESSÕES ---
# ESSENCIAL: Definir a secret_key logo após a criação da instância do Flask app
app.secret_key = os.getenv('SECRET_KEY')

# Adicione uma verificação robusta para a secret_key
if not app.secret_key:
    print("ATENÇÃO: FLASK_SECRET_KEY não definida no .env! Gerando uma para desenvolvimento. **NÃO USE EM PRODUÇÃO.**", file=sys.stderr)
    sys.stderr.flush()
    app.secret_key = os.urandom(24).hex() # Gera uma chave aleatória e a converte para string hexadecimal
    print(f"Chave gerada (apenas para DEBUG): {app.secret_key}", file=sys.stderr)
    sys.stderr.flush()
# --- FIM DA CHAVE SECRETA ---


# --- Classe de contexto para armazenar informações do usuário (se estiver usando) ---
# Mantenha esta classe se ela for usada em outras partes do seu código.
# Se for apenas para o login/sessão, a session do Flask é mais adequada.
class ContextManager:
    def __init__(self):
        self.context = {}

    def set_context(self, key, value):
        self.context[key] = value

    def get_context(self, key):
        return self.context.get(key, None)

    def clear_context(self, key=None):
        if key:
            if key in self.context:
                del self.context[key]
        else:
            self.context = {}

context = ContextManager()


# --- CHAVES DE API (Mantenha suas chaves de API aqui) ---
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

NEWSAPI_API_KEY = os.getenv('NEWSAPI_API_KEY')
if not NEWSAPI_API_KEY:
    print("AVISO: A chave da API do NewsAPI não foi encontrada. Notícias não funcionarão.", file=sys.stderr)
    sys.stderr.flush()
NEWSAPI_BASE_URL = "https://newsapi.org/v2/top-headlines"

GOOGLE_SEARCH_API_KEY = os.getenv('GOOGLE_SEARCH_API_KEY')
GOOGLE_CSE_ID = os.getenv('GOOGLE_CSE_ID')
if not GOOGLE_SEARCH_API_KEY or not GOOGLE_CSE_ID:
    print("AVISO: Chaves da API do Google Search (CSE) não configuradas. Pesquisa web não funcionará.", file=sys.stderr)
    sys.stderr.flush()
GOOGLE_SEARCH_BASE_URL = "https://www.googleapis.com/customsearch/v1"

YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
if not YOUTUBE_API_KEY:
    print("AVISO: Chave da API do YouTube não encontrada. Funções do YouTube não funcionarão.", file=sys.stderr)
    sys.stderr.flush()
YOUTUBE_BASE_URL = "https://www.googleapis.com/youtube/v3/search"

# --- Google Sheets Auth ---
SHEET_ID = os.getenv('SHEET_ID')
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'AI_Chatboy/credentials.json' # <-- VERIFIQUE ESTE CAMINHO!

gs_client = None
try:
    if os.path.exists(SERVICE_ACCOUNT_FILE):
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        gs_client = gspread.authorize(creds)
        print(f"Conexão com o Google Sheets estabelecida via arquivo: '{SERVICE_ACCOUNT_FILE}'.", file=sys.stderr)
        sys.stderr.flush()
    else:
        credentials_json_str = os.getenv('GOOGLE_SHEETS_CREDENTIALS')
        if credentials_json_str:
            credentials_info = json.loads(credentials_json_str)
            gs_client = gspread.service_account_from_dict(credentials_info)
            print("Conexão com o Google Sheets estabelecida via variável de ambiente.", file=sys.stderr)
            sys.stderr.flush()
        else:
            print("AVISO: Nem 'credentials.json' (ou nome do arquivo especificado) nem 'GOOGLE_SHEETS_CREDENTIALS' foram encontrados. Funções do Google Sheets não funcionarão.", file=sys.stderr)
            sys.stderr.flush()
except Exception as e:
    print(f"ERRO: Não foi possível conectar ao Google Sheets. Verifique suas credenciais. Erro: {e}", file=sys.stderr)
    sys.stderr.flush()

DEFAULT_CITY = "Rio de Janeiro"

# ... (o restante do seu código, dicionários de diálogos, funções auxiliares, etc.) ...

# --- Dicionários de diálogos e respostas ---
# (Mantidos como estavam, mas a lógica de uso será no get_response)
dialogues = {
    "Saudacao": [
        "Oi! Como posso te ajudar? 😊",
        "Olá! Tudo bem?",
        "Seja bem-vindo! Como posso ajudar hoje?",
        "Meu nome é ChatBoy, seu assistente virtual!"
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
    "qual e seu nome": ["Meu nome é ChatBoy!", "Sou o ChatBoy, seu assistente virtual!"],
    "adeus": ["Até logo!", "Tchau! Volte sempre!"],
    "qual e sua idade": ["Eu nasci em 2025, ainda estou crescendo!", "Tenho poucos meses de vida digital!"],
    "qual e sua comida favorita": ["Adoro pizza!", "Minha comida favorita é pizza!"],
    "qual e seu hobby": ["Gosto de aprender coisas novas!", "Meu hobby é ajudar as pessoas!"],
    "eu gosto de programar": ["Programar é incrível!", "Programar é uma ótima habilidade!"],
    "me fale sobre voce": [
        "Sou um assistente virtual criado para ajudar!",
        "Sou um chatbot treinado em várias áreas, pronto para conversar!"
    ],
    "me fale sobre o clima": [], # Removido, pois a função get_weather_info lida com isso.
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
    # Notícias serão tratadas por get_entertainment_news
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
if "me fale sobre ia" not in responses: # Convertido para minúsculas
    responses["me fale sobre ia"] = [
        "Inteligência Artificial é um campo que estuda como criar máquinas que podem simular a inteligência humana.",
        "A IA está presente em muitos aspectos do nosso dia a dia, desde assistentes virtuais até sistemas de recomendação."
    ]
if "me fale sobre machine learning" not in responses:
    responses["me fale sobre machine learning"] = [
        "Machine Learning é uma técnica dentro da IA que permite que sistemas aprendam e melhorem com a experiência.",
        "É usado em muitas aplicações, como reconhecimento de voz, visão computacional e sistemas de recomendação."
    ]
if "sobre mim" not in responses:
    responses["sobre voce"] = [ # Assumi que "sobre mim" se refere ao bot, então "sobre voce"
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
        "O Flamengo tem uma rica história e muitos títulos. Qual é o seu jogador favorito, inclusive, O jogo do Flamengo X Chelsea ontem foi lendário!"
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

# --- IDs de Canais do YouTube (para canais populares, para evitar busca API inicial) ---
YOUTUBE_CHANNEL_IDS = {
    "pewdiepie": "UC-lHJZR3GqXM24_Vd_AJX5w",
    "felipe neto": "UC5p0_Bla8wz31Q1g2dM_7fg",
    "nintendo": "UCqO7_pY_eR1iYQ-oSh_BBYQ",
    "cellbit": "UCm00oYq43R71L5T2fB-zT_g",
    # Adicione mais youtubers aqui que você quer que sejam encontrados rapidamente
}


# --- Funções auxiliares ---
def normalize_text(text):
    text = text.strip().lower()
    text = unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode("utf-8")
    return text

def get_weather_info(city_name=None):
    if not OPENWEATHER_API_KEY:
        return {"response": "Desculpe, a chave da API do OpenWeatherMap não está configurada.", "action": "none"}

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

            return {"response": (f"O clima em {city_name_returned} está {description}, "
                                 f"com temperatura de {temp:.1f}°C e sensação térmica de {feels_like:.1f}°C."), "action": "none"}
        else:
            return {"response": f"Não consegui encontrar informações climáticas para '{city_name}'. Poderia verificar o nome da cidade?", "action": "none"}

    except requests.exceptions.RequestException as e:
        print(f"Erro ao conectar com a API do OpenWeatherMap: {e}")
        return {"response": "Desculpe, estou com problemas para acessar as informações do clima no momento.", "action": "none"}
    except KeyError:
        return {"response": f"Não consegui encontrar informações climáticas detalhadas para '{city_name}'. Tente novamente mais tarde.", "action": "none"}

def get_entertainment_news(topic=None):
    if not NEWSAPI_API_KEY:
        return {"response": "Desculpe, a chave da API do NewsAPI não está configurada.", "action": "none"}

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
                return {"response": f"Aqui estão algumas notícias sobre {topic} para você:\n" + "\n".join(news_list), "action": "none"}
            else:
                return {"response": "Aqui estão as principais notícias de entretenimento:\n" + "\n".join(news_list), "action": "none"}
        else:
            if topic:
                return {"response": f"Não consegui encontrar notícias recentes sobre '{topic}' no momento.", "action": "none"}
            else:
                return {"response": "Não consegui encontrar notícias de entretenimento recentes no momento.", "action": "none"}

    except requests.exceptions.RequestException as e:
        print(f"Erro ao conectar com a API da NewsAPI: {e}")
        return {"response": "Desculpe, estou com problemas para acessar as notícias no momento.", "action": "none"}
    except KeyError:
        return {"response": "Desculpe, não consegui processar as informações de notícias. Tente novamente mais tarde.", "action": "none"}


def search_web(query):
    if not GOOGLE_SEARCH_API_KEY or not GOOGLE_CSE_ID:
        return {"response": "Desculpe, a funcionalidade de pesquisa na web não está configurada corretamente.", "action": "none"}

    params = {
        "key": GOOGLE_SEARCH_API_KEY,
        "cx": GOOGLE_CSE_ID,
        "q": query,
        "num": 5,
        "hl": "pt",
    }

    try:
        response = requests.get(GOOGLE_SEARCH_BASE_URL, params=params)
        response.raise_for_status()
        search_results = response.json()

        items = search_results.get("items")
        if items:
            markdown_results = []
            for i, item in enumerate(items, 1):
                title = item.get("title", "Sem título")
                link = item.get("link", "#")
                snippet = item.get("snippet", "")
                markdown_results.append(
                    f"**{i}. [{title}]({link})**\n> {snippet}"
                )
            markdown_response = (
                f"🔎 **Resultados para:** `{query}`\n\n"
                + "\n\n".join(markdown_results)
                + "\n\nSe quiser mais detalhes, clique nos títulos acima. 😊"
            )
            return {"response": markdown_response, "action": "none"}

        else:
            return {"response": "Não encontrei resultados para a sua pesquisa na web no momento.", "action": "none"}

    except requests.exceptions.RequestException as e:
        print(f"Erro ao conectar com a API do Google Search: {e}")
        return {"response": "Desculpe, estou com problemas para pesquisar na web agora. Pode ser um erro na sua chave ou no ID do CSE, ou o limite de requisições foi atingido.", "action": "none"}
    except Exception as e:
        print(f"Erro inesperado na pesquisa web: {e}")
        return {"response": "Desculpe, houve um erro ao processar sua pesquisa na web.", "action": "none"}
def get_latest_youtube_video(channel_name_input):
    if not YOUTUBE_API_KEY:
        return {"response": "Desculpe, a funcionalidade do YouTube não está configurada corretamente.", "action": "none"}

    channel_id = YOUTUBE_CHANNEL_IDS.get(channel_name_input.lower())

    # Se o ID não estiver mapeado, tenta encontrar o canal pela API de Busca
    if not channel_id:
        print(f"Tentando buscar ID do canal '{channel_name_input}' via YouTube API...")
        search_params = {
            "key": YOUTUBE_API_KEY,
            "q": channel_name_input,
            "type": "channel",
            "part": "snippet",
            "maxResults": 1
        }
        try:
            search_response = requests.get(YOUTUBE_BASE_URL, params=search_params)
            search_response.raise_for_status()
            search_data = search_response.json()
            items = search_data.get("items")
            if items:
                channel_id = items[0]["id"]["channelId"]
                print(f"ID do canal '{channel_name_input}' encontrado: {channel_id}")
            else:
                print(f"Não encontrei o canal '{channel_name_input}' na busca da API do YouTube.")
                return {"response": f"Não consegui encontrar o canal '{channel_name_input}'. Por favor, verifique o nome ou tente um nome mais específico.", "action": "none"}
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar ID do canal no YouTube API: {e}")
            return {"response": "Desculpe, estou com problemas para acessar o YouTube agora para encontrar o canal.", "action": "none"}
        except Exception as e:
            print(f"Erro inesperado ao buscar ID do canal: {e}")
            return {"response": "Desculpe, houve um erro ao processar a busca do canal no YouTube.", "action": "none"}

    if not channel_id:
        return {"response": f"Não consegui determinar o ID do canal para '{channel_name_input}'.", "action": "none"}

    # Com o channel_id, busca o vídeo mais recente
    params = {
        "key": YOUTUBE_API_KEY,
        "channelId": channel_id,
        "part": "snippet",
        "order": "date",
        "type": "video",
        "maxResults": 1
    }

    try:
        response = requests.get(YOUTUBE_BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()

        videos = data.get("items")
        if videos:
            video = videos[0]["snippet"]
            video_id = videos[0]["id"]["videoId"]
            video_title = video.get("title", "Título indisponível")
            channel_title = video.get("channelTitle", "Canal desconhecido")
            video_url = f"https://www.youtube.com/watch?v={video_id}"

            # Salva no contexto para a próxima resposta do usuário
            context.set_context("youtube_redirect_pending", True)
            context.set_context("youtube_video_url", video_url)
            context.set_context("youtube_video_title", video_title)

            return {
    "success": True,
    "response": (
        f"🎬 **Vídeo mais recente de [{channel_title}]({video_url})**\n\n"
        f"**Título:** {video_title}\n\n"
        f"🔗 [Assista agora]({video_url})\n\n"
        f"Você deseja ser redirecionado para o vídeo?"
    ),
    "action": "ask_for_youtube_redirect",
    "video_url": video_url,
    "video_title": video_title,
    "channel_title": channel_title
}
        else:
            return {"response": f"Não encontrei vídeos recentes para o canal '{channel_name_input}'. O canal pode não ter vídeos públicos ou o nome está incorreto.", "action": "none"}
    except requests.exceptions.RequestException as e:
        print(f"Erro ao conectar com a API do YouTube para buscar vídeos: {e}")
        return {"response": "Desculpe, estou com problemas para acessar o YouTube agora para buscar vídeos.", "action": "none"}
    except Exception as e:
        print(f"Erro inesperado ao buscar vídeo do YouTube: {e}")
        return {"response": "Desculpe, houve um erro ao processar sua solicitação de vídeo.", "action": "none"}


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
def get_response(user_message, context=None):
    user_message_normalized = normalize_text(user_message)
    if not context:
        context = ContextManager()
    # Programar feedback no chat
    if user_message_normalized.startswith("tive uma ideia:"): # Apenas ajustei o espaço para consistência
        idea = user_message[len("tive uma ideia:"):].strip()

        if not idea:
            return {"response": "Por favor, descreva sua ideia após 'tive uma ideia:'.", "action": "none"}
        
        # --- COMEÇO DA LÓGICA DE SALVAR FEEDBACK NO BANCO DE DADOS ---
        conn = None
        cur = None
        try:
            # 1. Obter o user_id do usuário logado
            # Usamos g.user para acessar o usuário logado, que é carregado em @app.before_request
            if not g.user:
                return {"response": "Desculpe, você precisa estar logado para enviar uma ideia.", "action": "none"}
            
            user_id = g.user['id'] # Pega o ID do dicionário g.user

            conn = get_db_connection()
            cur = conn.cursor()

            # 2. Verificar se a ideia já existe para este usuário
            cur.execute(
                "SELECT id FROM feedback WHERE user_id = %s AND message = %s",
                (user_id, idea)
            )
            existing_idea = cur.fetchone()

            if existing_idea:
                return {"response": "Você já enviou essa ideia antes. Por favor, tente outra.", "action": "none"}
            else:
                # 3. Inserir a nova ideia no banco de dados
                cur.execute(
                    "INSERT INTO feedback (user_id, message) VALUES (%s, %s)",
                    (user_id, idea)
                )
                conn.commit() # Salva a transação no banco de dados
                return {"response": "Ótima ideia! Vou anotar isso.", "action": "none"}

        except Exception as e:
            # Em caso de erro, desfaz a transação se houver uma conexão ativa
            if conn:
                conn.rollback()
            print(f"ERRO ao salvar feedback no banco de dados: {e}", file=sys.stderr)
            sys.stderr.flush()
            return {"response": "Desculpe, não consegui salvar sua ideia. Tente novamente mais tarde.", "action": "none"}
        finally:
            # Garante que o cursor e a conexão sejam fechados
            if cur:
                cur.close()
            if conn:
                conn.close()
    match_compare = re.match(r"comparar prec[co|cos]{1,2} (de|do|da) (.+)", user_message_normalized)
    if match_compare:
        game = match_compare.group(2).strip()
        if game:
            markdown = get_game_price_comparison(game)
            return {"response": markdown, "action": "none"}
        else:
            return {"response": "Qual jogo você quer comparar os preços?", "action": "none"}

    # --- Trigger para promoções ---
    match_promo = re.match(r"(tem )?promoc[aão]{2,3}( de| do| da)? (.+)", user_message_normalized)
    if match_promo:
        game = match_promo.group(3).strip()
        if game:
            markdown = get_game_deals(game)
            return {"response": markdown, "action": "none"}
        else:
            return {"response": "Qual jogo você quer ver as promoções?", "action": "none"}
        
    if user_message_normalized.endswith("e bom?"):
        topic = user_message_normalized[:-len("e bom?")].strip()
        query_for_search = f"{topic} é bom?"
        result = search_web(query_for_search)
    # Adiciona um título markdown bonito
        if "response" in result:
            result["response"] = (
            f"## 🤔 {topic.title()} é bom?\n\n"
            + result["response"]
            )
        return result
    
    # --- Gerenciamento de Contexto para "Sim/Não" do YouTube ---
    if context.get_context("youtube_redirect_pending"):
        if "sim" in user_message_normalized:
            video_url = context.get_context("youtube_video_url")
            video_title = context.get_context("youtube_video_title")
            context.clear_context() # Limpa todo o contexto após a decisão
            return {
                "response": f"Ótimo! Redirecionando para o vídeo '{video_title}'.",
                "action": "redirect_to_youtube",
                "url": video_url
            }
        elif "nao" in user_message_normalized or "não" in user_message_normalized:
            context.clear_context() # Limpa todo o contexto
            return {"response": "Ok, entendi. Se precisar de mais alguma coisa, é só chamar!", "action": "none"}
        else:
            return {"response": "Desculpe, não entendi sua resposta. Você gostaria de ser redirecionado para o vídeo (sim/não)?", "action": "ask_for_youtube_redirect"}
    
    # --- Lógica para YouTube (Vídeo Mais Recente) ---
    youtube_triggers = ["lancou video do", "qual e o video mais recente do", "lancou video novo do", "qual o video mais novo do"]
    for trigger in youtube_triggers:
        if user_message_normalized.startswith(trigger):
            youtuber_name = user_message[len(trigger):].strip()
            if youtuber_name:
                video_info = get_latest_youtube_video(youtuber_name)
                # get_latest_youtube_video já retorna o dicionário formatado
                if video_info.get("success"):
                    # Se for sucesso, já setamos o contexto dentro de get_latest_youtube_video e a resposta já está pronta
                    return video_info 
                else:
                    return video_info # Retorna o erro direto da função
            else:
                return {"response": "De qual youtuber você gostaria de saber o vídeo mais recente?", "action": "none"}

    # --- Lógica para o Clima ---
    if "clima" in user_message_normalized or "previsao do tempo" in user_message_normalized:
        city = None
        match_city = re.search(r'(?:em|para)\s+([a-zA-ZáéíóúÁÉÍÓÚçÇ\s]+)', user_message_normalized)
        if match_city:
            city = match_city.group(1).strip()
        
        return get_weather_info(city)

    # --- Placar de Jogos ("quanto foi") ---
    if user_message_normalized.startswith("quanto foi "):
        query_game_score = user_message[len("quanto foi "):].strip()
        full_query = f"{query_game_score} placar resultados jogo"
        return search_web(full_query)

    # --- Notícias de Entretenimento ---
    news_keywords = ["noticias", "notícias", "ultimas noticias", "ultimas notícias", "novidades"]
    entertainment_topics = ["filmes", "series", "séries", "jogos", "games", "musica", "música", "celebridades", "cultura pop"]
    is_news_query = any(keyword in user_message_normalized for keyword in news_keywords)
    if is_news_query:
        topic = None
        for et_topic in entertainment_topics:
            if et_topic in user_message_normalized:
                topic = et_topic
                break
        return get_entertainment_news(topic)
    
    # --- Datas de Lançamento / Pesquisa na Web ("quando vai", "que ano lança", "data de lançamento") ---
    launch_date_triggers = ["quando vai", "que ano lanca o", "data de lancamento"]
    for trigger in launch_date_triggers:
        if user_message_normalized.startswith(trigger):
            query_for_search = user_message[len(trigger):].strip()
            if query_for_search:
                return search_web(query_for_search + " data de lançamento")
            else:
                return {"response": "Você gostaria de saber a data de lançamento de quê?", "action": "none"}

    # --- "me fale sobre" (tópicos conhecidos ou busca na web) ---
    if user_message_normalized.startswith("me fale sobre "):
        query_for_search = user_message[len("me fale sobre "):].strip()
        query_normalized_for_check = normalize_text(query_for_search)
        
        found_in_responses = False
        for k_topic in responses.keys(): # Iterar sobre as chaves normalizadas
            if normalize_text(k_topic).startswith(query_normalized_for_check):
                if responses[k_topic]: # Verifica se a lista de respostas não está vazia
                    return {"response": random.choice(responses[k_topic]), "action": "none"}
                # Se a lista estiver vazia, pode tentar uma busca na web ou fallback
                # Por exemplo, "me fale sobre o clima" estava vazio e agora é tratado pela função de clima.
                found_in_responses = True
                break
    
        
        if not found_in_responses: # Se não encontrou uma resposta interna, tente a web
            return search_web(query_for_search)

    sorted_responses_keys = sorted(responses.keys(), key=len, reverse=True)
    for key in sorted_responses_keys:
        if normalize_text(key) in user_message_normalized and responses[key]:
            return {"response": random.choice(responses[key]), "action": "none"}

    sorted_dialogues_keys = sorted(dialogues.keys(), key=len, reverse=True)
    for key in sorted_dialogues_keys:
        if normalize_text(key) in user_message_normalized and dialogues[key]:
            return {"response": random.choice(dialogues[key]), "action": "none"}

    # --- Resposta Padrão se nenhuma condição for atendida ---
    default_responses = dialogues["ajuda"] + dialogues["Saudacao"] # Usa algumas respostas comuns
    return {"response": random.choice(default_responses), "action": "none"}

# --- Upload Excel endpoint ---
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True) # Garante que a pasta 'uploads' exista

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def dataframe_to_markdown_analysis(df):
    # Exemplo de análise: shape, colunas, tipos, amostra, estatísticas
    md = []
    md.append(f"## 📊 Análise do Arquivo\n")
    md.append(f"- **Linhas:** {df.shape[0]}")
    md.append(f"- **Colunas:** {df.shape[1]}")
    md.append(f"- **Colunas:** {', '.join(df.columns)}\n")
    md.append("### Primeiras linhas:\n")
    md.append("---\n")
    md.append(df.head(5).to_markdown(index=False))
    md.append("\n### Estatísticas descritivas:\n")
    md.append("---\n")
    md.append(df.describe(include='all').to_markdown())
    return "\n".join(md)

@app.route('/upload_excel', methods=['POST'])
def upload_excel_route(): # Renomeado para evitar conflito com 'upload_excel' de pandas
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado.'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nome de arquivo vazio.'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            if filename.lower().endswith('.csv'):
                df = pd.read_csv(filepath)
            else:
                df = pd.read_excel(filepath)

# Corrige colunas de data/hora para string
            for col in df.columns:
                if pd.api.types.is_datetime64_any_dtype(df[col]):
                    df[col] = df[col].astype(str)
            df = df.fillna("") # Preenche valores NaN com string vazia

# Corrige colunas de data/hora para string
        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'error': f'Erro ao ler o arquivo Excel: {e}'}), 400
        
        if not gs_client:
            if os.path.exists(filepath):
                os.remove(filepath) # Remove o arquivo temporário mesmo em erro
            return jsonify({'error': 'Google Sheets não autenticado. Verifique suas credenciais.'}), 500
        
        try:
            # Opção 1: Criar uma nova planilha no Google Sheets com um nome baseado no arquivo + timestamp
            # Isso é mais seguro para evitar sobrescrever dados
            sheet_title = f'Upload_{filename.replace(".", "_")}_{datetime.now().strftime("%Y%m%d%H%M%S")}'
            sh = gs_client.create(sheet_title)
            worksheet = sh.sheet1 # Pega a primeira aba da nova planilha
            
            # Opção 2 (Alternativa): Atualizar uma planilha existente pelo nome/ID e aba
            # Se você quiser atualizar uma específica, o usuário precisaria enviar o ID/Nome da planilha e da aba
            # Por simplicidade e segurança, a criação de uma nova é mais direta para uploads.

            # Converte o DataFrame para uma lista de listas (incluindo cabeçalhos) para upload
            worksheet.update([df.columns.values.tolist()] + df.values.tolist())
            
            sheet_url = sh.url # Pega a URL da nova planilha criada
        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath) # Remove o arquivo temporário mesmo em erro
            return jsonify({'error': f'Erro ao criar ou preencher planilha no Google Sheets: {e}'}), 500
        
        # Remove o arquivo temporário após o upload bem-sucedido
        if os.path.exists(filepath):
            os.remove(filepath)
        analysis_md = dataframe_to_markdown_analysis(df)
        return jsonify({
            'message': 'Arquivo enviado e planilha criada com sucesso!',
            'sheet_url': sheet_url,
            'analysis': analysis_md
        })
    elif 'error' in responses:
        return jsonify({'error': 'Mensagem de erro'}), 500
    else:
        return jsonify({'error': 'Formato de arquivo inválido.'}), 400
    
import requests

def get_usd_brl():
    """Busca a cotação do dólar em relação ao real (BRL)."""
    try:
        # Usando a API AwesomeAPI (sem autenticação)
        cotacao = requests.get("https://economia.awesomeapi.com.br/json/last/USD-BRL").json()
        return float(cotacao["USDBRL"]["bid"])
    except Exception:
        return 5.0  # fallback para um valor aproximado

def get_game_price_comparison(title="Elden Ring"):
    """
    Busca as melhores ofertas do jogo nas principais lojas e retorna um markdown comparativo em real.
    """
    url = "https://www.cheapshark.com/api/1.0/deals"
    params = {
        "title": title,
        "pageSize": 10,
        "sortBy": "Price"
    }
    response = requests.get(url, params=params)
    data = response.json()

    if not data:
        return f"⚠️ Nenhuma promoção encontrada para '{title}'."

    # Cotação do dólar
    usd_brl = get_usd_brl()

    # Mapeia storeID para nome da loja
    stores_resp = requests.get("https://www.cheapshark.com/api/1.0/stores")
    stores = {store["storeID"]: store["storeName"] for store in stores_resp.json()}

    markdown = f"## 💸 Comparativo de preços para **{title}** (em real)\n\n"
    markdown += "| Loja | Preço (BRL) | Preço Normal (BRL) | Desconto | Link |\n"
    markdown += "|------|-------------|--------------------|----------|------|\n"

    # Mostra só uma oferta por loja (a melhor)
    best_deals = {}
    for game in data:
        store_id = game["storeID"]
        if store_id not in best_deals:
            best_deals[store_id] = game

    for store_id, game in best_deals.items():
        loja = stores.get(store_id, f"Loja {store_id}")
        preco = float(game['salePrice']) * usd_brl
        preco_normal = float(game['normalPrice']) * usd_brl
        desconto = f"{round(float(game['savings']))}%"
        link = f"[Abrir]({'https://www.cheapshark.com/redirect?dealID=' + game['dealID']})"
        markdown += f"| {loja} | R$ {preco:.2f} | R$ {preco_normal:.2f} | {desconto} | {link} |\n"

    markdown += "\n---\n"
    markdown += "_Os preços são aproximados e podem variar conforme a cotação do dólar. Clique em 'Abrir' para ir direto à oferta._"
    return markdown

def get_game_deals(title="Elden Ring"):
    url = "https://www.cheapshark.com/api/1.0/deals"
    params = {
        "title": title,
        "pageSize": 3,  # número de resultados
        "sortBy": "Savings"
    }
    response = requests.get(url, params=params)
    data = response.json()

    if not data:
        return f"⚠️ Nenhuma promoção encontrada para '{title}'."

    usd_brl = get_usd_brl()

    markdown = f"🎮 Promoções para **{title}** (valores em real):\n\n"
    for game in data:
        preco = float(game['salePrice']) * usd_brl
        preco_normal = float(game['normalPrice']) * usd_brl
        desconto = f"{round(float(game['savings']))}%"
        link = f"https://www.cheapshark.com/redirect?dealID={game['dealID']}"
        loja = game.get('storeID', 'Loja')
        markdown += (
            f"- **{game['title']}**\n"
            f"  - 💰 Preço: R$ {preco:.2f} (normal: R$ {preco_normal:.2f})\n"
            f"  - 💸 Desconto: {desconto}\n"
            f"  - 🔗 [Ver na loja]({link})\n"
            "---\n"
        )
    markdown += "\n_Valores aproximados, convertidos pela cotação atual do dólar._"
    return markdown

from flask import Flask, render_template, request, redirect, jsonify
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash

# Conexão com PostgreSQL
import os
import psycopg2
from dotenv import load_dotenv

# Certifique-se que load_dotenv() está sendo chamado antes de get_db_connection()
# Idealmente, no topo do seu app.py, como você já tem.
load_dotenv()

def get_db_connection():
    db_name = os.getenv('DATABASE')
    db_user = os.getenv('USER')
    db_password = os.getenv('PASSWORD') # CUIDADO: Não mantenha isso em produção!
    db_host = os.getenv('HOST')
    db_port = os.getenv('PORT')

    print(f"DEBUG: DATABASE (repr): {repr(db_name)}")
    print(f"DEBUG: USER (repr): {repr(db_user)}")
    print(f"DEBUG: PASSWORD (repr): {repr(db_password)}") # **IMPORTANTE PARA DEPURAR**
    print(f"DEBUG: HOST (repr): {repr(db_host)}")
    print(f"DEBUG: DB_PORT (repr): {repr(db_port)}")

    try:
        conn = psycopg2.connect(
            database=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
            # Opcional: client_encoding='UTF8' - menos provável de resolver se o erro é na string de entrada
        )
        return conn
    except Exception as e:
        print(f"*** ERRO NA CONEXÃO DO BANCO DE DADOS: {e} ***")
        raise # Re-levanta a exceção para que o Flask a capture

from flask import g

# --- Rota de Chat Principal ---
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")
    response_data = get_response(user_message)
    return jsonify(response_data)


# --- @app.before_request para carregar usuário logado ---
@app.before_request
def load_logged_in_user():
    user_id = session.get("user_id") # Pega o user_id da sessão
    if user_id is None:
        g.user = None # Se não há user_id na sessão, não há usuário logado
    else:
        conn = None # Inicializa conn e cur para garantir que estejam definidos no finally
        cur = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT id, username FROM users WHERE id = %s", (user_id,))
            user_data = cur.fetchone() # user_data será (id, username)
            if user_data:
                g.user = {"id": user_data[0], "username": user_data[1]}
            else:
                g.user = None # Se o user_id na sessão não corresponde a um usuário válido
                session.pop('user_id', None) # Limpa a sessão para evitar loops
                session.pop('username', None) # Limpa o username também
        except Exception as e:
            print(f"Erro em @before_request ao carregar usuário: {e}", file=sys.stderr)
            sys.stderr.flush()
            g.user = None # Garante que g.user é None em caso de erro
            session.pop('user_id', None) # Limpa a sessão para evitar erro persistente
            session.pop('username', None)
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()


# --- Rota Principal (index) ---
@app.route("/")
def index():
    # Agora, o username é obtido de g.user, que é carregado por @app.before_request
    username = g.user['username'] if g.user else None
    return render_template("index.html", username=username)

# --- Rota para Criar Perfil ---
@app.route("/create_profile", methods=["GET", "POST"])
def create_profile():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not username or not password or not confirm_password:
            return render_template("create_profile.html", message="Preencha todos os campos.")
        if password != confirm_password:
            return render_template("create_profile.html", message="As senhas não coincidem.")
        
        password_hash = generate_password_hash(password)
        conn = None
        cur = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, password_hash))
            conn.commit()
            return redirect(url_for('login_profile'))
        except psycopg2.errors.UniqueViolation:
            if conn:
                conn.rollback()
            return render_template("create_profile.html", message="Usuário já existe. Escolha outro nome de usuário.")
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Erro ao criar perfil: {e}", file=sys.stderr)
            sys.stderr.flush()
            return render_template("create_profile.html", message="Erro no cadastro. Tente novamente.")
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
    return render_template("create_profile.html")

# --- Rota de Login ---
@app.route("/login_profile", methods=["GET", "POST"])
def login_profile():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = None
        cur = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            # Selecione o ID, username e password_hash
            cur.execute("SELECT id, username, password_hash FROM users WHERE username = %s", (username,))
            user_data = cur.fetchone() # user_data agora será (id, username, password_hash)
            
            if user_data and check_password_hash(user_data[2], password): # user_data[2] é o password_hash
                user_id = user_data[0]
                logged_in_username = user_data[1]
                
                # Armazena o ID e o username na sessão
                session['user_id'] = user_id
                session['username'] = logged_in_username # Armazena o nome de usuário também

                return redirect(url_for('index')) # Redireciona para a página principal
            else:
                return render_template("login_profile.html", message="Credenciais inválidas!")
        except Exception as e:
            print(f"Erro durante o login: {e}", file=sys.stderr)
            sys.stderr.flush()
            return render_template("login_profile.html", message="Erro ao tentar fazer login. Tente novamente.")
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
    return render_template("login_profile.html")

# --- Nova Rota de Logout ---
@app.route("/logout")
def logout():
    session.pop('user_id', None)
    session.pop('username', None) # Remove o username da sessão também
    return redirect(url_for('login_profile'))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)


