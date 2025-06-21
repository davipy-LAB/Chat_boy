import random
import unicodedata
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

# Classe de contexto para armazenar informações do usuário
class Context:
    def __init__(self):
        self.context = {}

    def set_context(self, key, value):
        self.context[key] = value

    def get_context(self, key):
        return self.context.get(key, None)

# Inicializa o contexto
context = Context()
context.set_context("user_name", "ChatGuy")

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
        "O clima está ótimo hoje!",
        "Parece que vai chover mais tarde.",
        "Gosto de dias ensolarados, e você?",
        "Se quiser saber a previsão, posso ajudar!"
    ]
}

# Dicionário de respostas rápidas e perguntas frequentes
responses = {
    "tudo bem": ["Tudo ótimo! E você?", "Estou bem, obrigado!"],
    "Eu não" "Não tô bem": ["Sinto muito! O que posso fazer para ajudar?", "Estou aqui se você precisar conversar."],
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
    "me fale sobre o clima": ["O clima está ótimo hoje!", "Hoje está um dia lindo!"],
    "eu te amo": ["Eu também te amo! 💙", "Amo ajudar você!"],
    "qual e seu jogo favorito": ["Adoro The Witcher!", "Meu jogo favorito é The Witcher!"],
    "qual e seu filme favorito": ["Adoro Matrix!", "Meu filme favorito é Matrix!"],
    "qual e seu livro favorito": ["Adoro Harry Potter!", "Meu livro favorito é Harry Potter!"],
    "voce gosta de linguas": ["Sim, adoro aprender novas línguas!", "Línguas são fascinantes!"],
    "me ajude": ["Estou aqui para ajudar!", "Claro! O que você precisa?"],
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
    "qual a diferença entre IA e machine learning": [
        "IA é a inteligência artificial em geral, enquanto machine learning é um subcampo que ensina máquinas a aprender com dados.",
        "Machine learning é uma técnica dentro da IA que permite que sistemas aprendam e melhorem com a experiência."
    ],
    "Qual a diferença entre python e java": [
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
    "me indique uma série": [
        "Assista 'Stranger Things' ou 'Dark'!",
        "Gosto muito de 'Black Mirror'."
    ],
    "me conte uma piada": [
        "Por que o computador foi ao médico? Porque estava com um vírus! 😄",
        "O que o zero disse para o oito? Belo cinto!"
    ]
}

if "me fale sobre" in responses:
        responses["me fale sobre"].extend([
            "Você gostaria de saber mais sobre algum assunto específico?",
            "Posso falar sobre tecnologia, ciência, cultura pop e muito mais!"
        ])

if "me fale sobre tecnologia" not in responses:
    responses["me fale sobre tecnologia"] = [
        "Tecnologia é fascinante! Posso te ajudar com conceitos de programação, se quiser.",
        "Você gosta de inteligência artificial? É um campo incrível!"
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
        "A ciência é fascinante! Ela nos ajuda a entender o mundo ao nosso redor.",
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

# Função para obter a resposta da IA
def get_response(user_message):
    user_message = normalize_text(user_message)
    # Busca em respostas rápidas
    for key in responses:
        if key in user_message:
            return random.choice(responses[key])
    # Busca em diálogos temáticos
    for tema, lista in dialogues.items():
        if tema.lower() in user_message:
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