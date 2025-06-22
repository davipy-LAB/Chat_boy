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

if "historia do brasil" not in responses:
    responses["historia do brasil"] = [
        "A história do Brasil é rica e diversa, desde a época dos indígenas até a colonização portuguesa.",
        "Posso falar sobre eventos importantes, como a independência e a república!"
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
            for item in items:
                title = item.get("title")
                snippet = item.get("snippet")
                link = item.get("link")
                match_ano = re.search(r'\b(20[2-3][0-9])\b', snippet)
                match_mes_ano = re.search(r'(?:janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)\s*(?:de)?\s*(20[2-3][0-9])', snippet, re.IGNORECASE)
                if ("lançamento" in snippet.lower() or "data" in snippet.lower() or "release" in snippet.lower()):
                    if match_mes_ano:
                        return f"Pelo que encontrei, o {title.split(' - ')[0]} tem previsão de lançamento para {match_mes_ano.group(0)}. Mais detalhes: {link}"
                    elif match_ano:
                        return f"Pelo que encontrei, o {title.split(' - ')[0]} tem previsão de lançamento para {match_ano.group(0)}. Mais detalhes: {link}"
            first_item = items[0]
            return f"Não encontrei uma resposta exata, mas achei isto: '{first_item.get('snippet')}' (Fonte: {first_item.get('title')}). Veja mais: {first_item.get('link')}"
        else:
            return "Não encontrei resultados para a sua pesquisa na web no momento."

    except requests.exceptions.RequestException as e:
        print(f"Erro ao conectar com a API do Google Search: {e}")
        return "Desculpe, estou com problemas para pesquisar na web agora. Pode ser um erro na sua chave ou no ID do CSE, ou o limite de requisições foi atingido."
    except Exception as e:
        print(f"Erro inesperado na pesquisa web: {e}")
        return "Desculpe, houve um erro ao processar sua pesquisa na web."

def get_response(user_message):
    user_message_normalized = normalize_text(user_message)
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
        return get_weather_info(city)
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
            return search_web(query_for_search)
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
        if user_message_normalized.startswith(trigger):
            query_for_search = user_message[len(trigger):].strip()
            search_result = search_web(query_for_search)
            if trigger == "quando vai ":
                return "Entendo sua questão, segundo meus dados, segue uma analise: " + search_result
            else:
                return search_result
    for key in responses:
        if key in user_message_normalized:
            return random.choice(responses[key])
    for tema, lista in dialogues.items():
        if tema.lower() in user_message_normalized:
            return random.choice(lista)
    return "Desculpe, não entendi. Pode repetir?"

# --- Google Sheets Auth ---
def get_sheets_client():
    credentials_json_str = os.getenv('GOOGLE_SHEETS_CREDENTIALS')
    if credentials_json_str:
        credentials_info = json.loads(credentials_json_str)
        gc = gspread.service_account_from_dict(credentials_info)
        print("Google Sheets: Autenticado via variável de ambiente.")
    else:
        try:
            gc = gspread.service_account(filename='chatboy-463619-b295229e68c6.json')
            print("Google Sheets: Autenticado via arquivo local 'service_account.json'.")
        except FileNotFoundError:
            print("ERRO: O arquivo 'service_account.json' não foi encontrado.")
            return None
        except Exception as e:
            print(f"ERRO ao autenticar o Google Sheets via arquivo local: {e}")
            return None
    return gc

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
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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
        file.save(filepath)
        try:
            df = pd.read_excel(filepath)
        except Exception as e:
            os.remove(filepath)
            return jsonify({'error': f'Erro ao ler o arquivo Excel: {e}'}), 400
        if not gs_client:
            os.remove(filepath)
            return jsonify({'error': 'Google Sheets não autenticado.'}), 500
        try:
            sh = gs_client.create(f'Upload_{filename}')
            worksheet = sh.sheet1
            worksheet.update([df.columns.values.tolist()] + df.values.tolist())
            sheet_url = sh.url
        except Exception as e:
            os.remove(filepath)
            return jsonify({'error': f'Erro ao criar planilha no Google Sheets: {e}'}), 500
        os.remove(filepath)
        return jsonify({'message': 'Arquivo enviado e planilha criada com sucesso!', 'sheet_url': sheet_url})
    else:
        return jsonify({'error': 'Tipo de arquivo não suportado.'}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)