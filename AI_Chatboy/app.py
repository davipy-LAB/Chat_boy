import random
import unicodedata
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

# Respostas fixas iniciais (todas as chaves em minúsculas)
responses = {
    "oi": ["Olá! Como posso te ajudar?", "Oi! Tudo bem?"],
    "como voce esta": ["Estou bem, obrigado!", "Estou ótimo! E você?"],
    "qual e seu nome": ["Meu nome é ChatGuy!", "Sou o ChatGuy, seu assistente virtual!"],
    "adeus": ["Até logo!", "Tchau! Volte sempre!"],
    "pode me dizer outra coisa": ["O que mais deseja saber?", "Qual outra coisa que deseja saber?"],
    "qual e sua idade": ["Eu nasci em 2025, ainda estou crescendo!", "Eu nasci em 2025, ainda estou crescendo!"],
    "tudo bem?": ["Estou bem, obrigado!", "Estou ótimo! E você?"],
    "qual e sua comida favorita": ["Adoro pizza!", "Minha comida favorita é pizza!"],
    "qual e seu hobby": ["Gosto de aprender coisas novas!", "Meu hobby é ajudar as pessoas!"],
    "eu gosto de programar": ["Programar é incrível!", "Programar é uma ótima habilidade!"],
    "me fale sobre voce": ["Sou um assistente virtual criado para ajudar!", "Sou um chatbot criado para ajudar você!"],
    "me fale sobre o clima": ["O clima está ótimo hoje!", "Hoje está um dia lindo!"],
    "eu te amo": ["Eu também te amo!", "Amo ajudar você!"],
    "qual e seu jogo favorito": ["Adoro The Witcher!", "Meu jogo favorito é The Witcher!"],
    "qual e seu filme favorito": ["Adoro Matrix!", "Meu filme favorito é Matrix!"],
    "qual e seu livro favorito": ["Adoro Harry Potter!", "Meu livro favorito é Harry Potter!"],
    "voce gosta de linguas": ["Sim, adoro aprender novas línguas!", "Línguas são fascinantes!"],
    "Que legal!": ["Fico feliz que você ache isso!", "Isso é ótimo!"],
    "isso é incrível": ["Fico feliz que você ache isso!", "Isso é ótimo!"],
    "na moral": ["Sim, na moral!", "Com certeza!"],
    "Me ajude": ["Estou aqui para ajudar!", "Estou aqui para ajudar!"],
    "me ajuda": ["Claro! O que você precisa?", "Estou aqui para ajudar!"],
    "me ajuda com isso": ["Claro! O que você precisa?", "Estou aqui para ajudar!"],
    "Estou triste": ["Sinto muito! O que posso fazer para ajudar?", "Estou aqui se você precisar conversar."],
    "Estou feliz": ["Fico feliz em ouvir isso!", "Que bom! Continue assim!"],
    "Estou cansado": ["Isso é uma pena, vá descansar! Qualquer coisa estou aqui", "Que pena! Quer falar sobre isso?"],
}

# Lista de frases comuns (algumas reais, outras para completar a quantidade)
common_phrases = [
    "bom dia", "boa tarde", "boa noite", "tudo bem", "tudo bom", "como vai", "como voce esta",
    "e ai", "fala ae", "o que conta", "como andam as coisas", "qual o seu hobby", "gosta de programar",
    "qual seu jogo", "qual seu filme", "o que voce faz", "me conta algo novo", "estou com fome",
    "vamos conversar", "tudo certo", "tempo bom hoje", "que legal", "isso é incrível", "na moral", "você pode me ajudar?",
    # Adicione mais frases conforme necessário
]

# Caso a lista tenha menos de 200 itens, duplicamos até atingir 200
while len(common_phrases) < 200:
    common_phrases += common_phrases

# Garantir que temos exatamente 200 elementos
common_phrases = common_phrases[:200]

# Cria um dicionário com as frases comuns e respostas padrão
extra_responses = {}
for phrase in common_phrases:
    extra_responses[phrase] = [f"Resposta padrão para '{phrase}'"]

# Atualiza o dicionário de respostas com os extras
responses.update(extra_responses)

# Função para normalizar strings (remove acentos e coloca em minúsculas)
def normalize_text(text):
    text = text.strip().lower()  # Remove espaços e coloca em minúsculas
    text = unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode("utf-8")  # Remove acentos
    return text

# Função para obter a resposta da IA
def get_response(user_message):
    user_message = normalize_text(user_message)  # Normaliza a mensagem do usuário
    for key in responses:
        if key in user_message:  # Verifica se alguma chave está na mensagem
            return random.choice(responses[key])
    return "Desculpe, não entendi. Pode repetir?"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")
    response = get_response(user_message)  # Obtém a resposta da IA
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
