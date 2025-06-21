import random
import os
from dotenv import load_dotenv
import unicodedata
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import re

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

# --- CHAME load_dotenv() AQUI! ---
load_dotenv()

@app.route('/')
def index():
    return render_template('index.html')

# --- CHAVE DA API E CONFIGURAÇÕES DO CLIMA ---
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# --- CHAVE DA API E CONFIGURAÇÕES DE NOTÍCIAS (NEWSAPI.ORG) ---
NEWSAPI_API_KEY = os.getenv('NEWSAPI_API_KEY')
if not NEWSAPI_API_KEY:
    raise ValueError("A chave da API do NewsAPI não foi encontrada. Por favor, defina a variável de ambiente NEWSAPI_API_KEY.")
NEWSAPI_BASE_URL = "https://newsapi.org/v2/top-headlines"

# --- NOVAS CHAVES DA API E CONFIGURAÇÕES DO GOOGLE CUSTOM SEARCH ---
GOOGLE_SEARCH_API_KEY = os.getenv('GOOGLE_SEARCH_API_KEY')
GOOGLE_CSE_ID = os.getenv('GOOGLE_CSE_ID')
GOOGLE_SEARCH_BASE_URL = "https://www.googleapis.com/customsearch/v1"

DEFAULT_CITY = "Rio de Janeiro"

# Dicionário de diálogos temáticos
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
        # Estas respostas serão substituídas pela função de clima
        "Buscando informações sobre o clima...",
        "Um momento, estou verificando o clima para você."
    ],
    "noticias": [ # Adicionado para a intenção de notícias gerais
        "Buscando as últimas notícias de entretenimento para você...",
        "Um instante, estou verificando as notícias do mundo do entretenimento."
    ]
}

# Dicionário de respostas rápidas e perguntas frequentes
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
        "O Sol representa 99,86% da massa do Sistema Solar!",
        "Cara, você sabia que a palavra 'hate' não vem do inglês? Ela é uma palavra de origem Proto-germânica! 😄 ",
        "Você sabia que o Latim tinha mais de 100 variantes? É verdade! Ele era falado em várias regiões com sotaques e dialetos diferentes! Por conta do latim vulgar ter sido totalmente moldável pelo povo hahaha",
    ],
    "quem te criou": [
        "Fui criado por desenvolvedores apaixonados por IA!",
        "Sou fruto de muito código e aprendizado de máquina."
    ],
    "voce gosta de tecnologia": [
        "Sou movido por tecnologia! 🚀",
        "Tecnologia é fascinante, não acha?",
        "Posso ajudar com conceitos de programação, se quiser."
    ],
    "qual a diferenca entre ia e machine learning": [
        "IA é a inteligência artificial em geral, enquanto machine learning é um subcampo que ensina máquinas a aprender com dados.",
        "Machine learning é uma técnica dentro da IA que permite que sistemas aprendam e melhorem com a experiência."
    ],
    "qual a diferenca entre python e java": [
        "Python é uma linguagem de programação de alto nível, fácil de aprender e muito usada em ciência de dados e IA. Java é mais robusto, orientado a objetos e amplamente usado em desenvolvimento de aplicativos corporativos.",
        "Python é conhecido por sua simplicidade e legibilidade, enquanto Java é mais estruturado e usado em aplicações empresariais."
    ],
    "me indique um filme": [
        "Que tal assistir 'A Origem' ou 'Interestelar'?",
        "Recomendo 'O Jogo da Imitação'!"
    ],
    "me indique um livro": [
        "Leia '1984' de George Orwell!",
        "Recomendo 'O Pequeno Príncipe'."
    ],
    "me recomende um jogo": [
        "Você é um jogador de RPG? The Witcher 3 é uma ótima escolha! (ps: se você for oldschool, recomendo o primeiro jogo da série também!)",
        "Histórias sombrias? é pra já! Recomendo 'Omori' ou 'Hollow Knight'.",
        "Você já jogou 'Celeste' ou 'The Last of Us'? Histórias de arrepiar!",
        "Você é criativo? Experimente jogar Minecraft!",
        "Que tal jogar 'Stardew Valley' ou 'Terraria'? Se vocÊ gosta de algo mais relaxante, esses jogos são ótimos!",
        "Se você gosta de jogos de estratégia, recomendo 'Civilization VI' ou 'Age of Empires II'.",
    ],
    "me indique uma serie": [
        "Assista 'Stranger Things' ou 'Dark'!",
        "Gosto muito de 'Black Mirror'."
    ],
    "me conte uma piada": [
        "Por que o computador foi ao médico? Porque estava com um vírus! 😄",
        "O que o zero disse para o oito? Belo cinto!"
    ],
    "noticias": [], # Deixamos vazio, será tratado pela lógica de intenção
    "ultimas noticias": [],
    "noticias de hoje": [],
    "noticias de entretenimento": [],
    "noticias de filmes": [],
    "noticias de series": [],
    "noticias de jogos": [],
    "noticias de musica": []
}

if "me fale sobre" in responses:
    responses["me fale sobre"].extend([
        "Você gostaria de saber mais sobre algum assunto específico?",
        "Posso falar sobre tecnologia, ciência, cultura pop e muito mais!"
    ])

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

if "historia do brasil" not in responses:
    responses["historia do brasil"] = [
        "A história do Brasil é rica e diversa, desde a época dos indígenas até a colonização portuguesa.",
        "Posso falar sobre eventos importantes, como a independência e a república!"
    ]

# Função para normalizar strings (remove acentos e coloca em minúsculas)
def normalize_text(text):
    text = text.strip().lower()
    text = unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode("utf-8")
    return text

# Função para obter informações do clima usando a API do OpenWeatherMap
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
# --- FUNÇÃO PARA OBTER NOTÍCIAS DE ENTRETENIMENTO (NEWSAPI) ---
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

# --- FUNÇÃO PARA PESQUISAR NA WEB (GOOGLE CUSTOM SEARCH) ---
def search_web(query):
    if not GOOGLE_SEARCH_API_KEY or not GOOGLE_CSE_ID:
        return "Desculpe, a funcionalidade de pesquisa na web não está configurada corretamente."

    params = {
        "key": GOOGLE_SEARCH_API_KEY,
        "cx": GOOGLE_CSE_ID,
        "q": query,
        "num": 5, # Número de resultados a serem retornados
        "hl": "pt", # Define o idioma dos resultados como português
        "dateRestrict": "y1" # Restringe os resultados ao último ano (mais recente)
    }

    try:
        response = requests.get(GOOGLE_SEARCH_BASE_URL, params=params)
        response.raise_for_status() # Levanta um erro para status HTTP ruins
        search_results = response.json()

        items = search_results.get("items")
        if items:
            # Tenta encontrar a informação mais relevante
            # Para "GTA VI", procurar por data de lançamento em snippets é um bom começo
            
            for item in items:
                title = item.get("title")
                snippet = item.get("snippet")
                link = item.get("link")

                # Lógica simplificada: se "lançamento" ou "data" estiver no snippet
                # e o snippet não for muito curto, e tiver um ano, pode ser útil.
                match_ano = re.search(r'\b(20[2-3][0-9])\b', snippet) # Procura por anos como 202X
                match_mes_ano = re.search(r'(?:janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)\s*(?:de)?\s*(20[2-3][0-9])', snippet, re.IGNORECASE)
                
                # Prioriza a data completa (mês e ano), depois só o ano
                if ("lançamento" in snippet.lower() or "data" in snippet.lower() or "release" in snippet.lower()):
                    if match_mes_ano:
                        return f"Pelo que encontrei, o {title.split(' - ')[0]} tem previsão de lançamento para {match_mes_ano.group(0)}. Mais detalhes: {link}"
                    elif match_ano:
                        return f"Pelo que encontrei, o {title.split(' - ')[0]} tem previsão de lançamento para {match_ano.group(0)}. Mais detalhes: {link}"
            
            # Se não encontrou uma data específica, retorna o primeiro snippet relevante
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


# Função para obter a resposta da IA
# Função para obter a resposta da IA
def get_response(user_message):
    user_message_normalized = normalize_text(user_message)

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
        return get_weather_info(city)

    # --- Lógica para Notícias de Entretenimento ---
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

    # --- Lógica para "me fale sobre" (PRIORIDADE ALTA, para tópicos conhecidos) ---
    # Verifica se a frase começa com "me fale sobre"
    if user_message_normalized.startswith("me fale sobre "):
        query_for_search = user_message[len("me fale sobre "):].strip()
        known_topics = [
            "tecnologia", "ia", "machine learning", "musica", "arte", "esportes",
            "jesus", "deus", "politica", "economia", "ciencia", "historia do brasil",
            "voce" # Adicione 'voce' aqui para "me fale sobre voce"
        ]
        
        # Normaliza a query para comparar com os tópicos conhecidos
        query_normalized_for_check = normalize_text(query_for_search)

        is_known_topic = False
        for k_topic in known_topics:
            # Verifica se o tópico conhecido está contido na query
            if k_topic in query_normalized_for_check:
                is_known_topic = True
                break
        
        if not is_known_topic: # Se NÃO for um tópico conhecido, pesquisa na web
            return search_web(query_for_search)
        # Se for um tópico conhecido, o código continua para as respostas fixas abaixo.


    # --- Lógica para Outras Pesquisas na Web (Google Custom Search) ---
    # Gatilhos específicos, mais longos devem vir primeiro na lista para serem verificados
    search_triggers_web = [
        "quando vai ", # NOVO: Para a lógica "Entendo sua questão..."
        "que ano lança ",
        "data de lançamento ",
        "qual ",
        "quando ",
        "quem é ",
        "o que é ",
        "onde é "
    ]
    # Classifica os gatilhos por tamanho (do maior para o menor)
    search_triggers_web.sort(key=len, reverse=True)

    for trigger in search_triggers_web:
        if user_message_normalized.startswith(trigger):
            query_for_search = user_message[len(trigger):].strip()
            
            search_result = search_web(query_for_search)
            
            # Adiciona a frase prefixada apenas para o gatilho "quando vai "
            if trigger == "quando vai ":
                return "Entendo sua questão, segundo meus dados, segue uma analise: " + search_result
            else:
                # Para todos os outros gatilhos de busca, retorna o resultado direto
                return search_result

    # --- Busca em respostas rápidas (este bloco só será alcançado se NENHUMA lógica acima foi ativada) ---
    for key in responses:
        if key in user_message_normalized:
            return random.choice(responses[key])

    # --- Busca em diálogos temáticos (este bloco só será alcançado se NENHUMA lógica acima foi ativada) ---
    for tema, lista in dialogues.items():
        if tema.lower() in user_message_normalized:
            return random.choice(lista)

    return "Desculpe, não entendi. Pode repetir?"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")
    response = get_response(user_message)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)