import random
import unicodedata
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

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
    "Estou cansado": ["Isso é uma pena, vá descansar! Qualquer coisa estou aqui", "Que pena! Quer falar sobre isso?"],}
# Lista de frases comuns (algumas reais, outras para completar a quantidade)
common_phrases = [
    "bom dia", "boa tarde", "boa noite", "tudo bem", "tudo bom", "como vai", "como voce esta",
    "e ai", "fala ae", "o que conta", "como andam as coisas", "qual o seu hobby", "gosta de programar",
    "qual seu jogo", "qual seu filme", "o que voce faz", "me conta algo novo", "estou com fome",
    "vamos conversar", "tudo certo", "tempo bom hoje", "que legal", "isso é incrível", "na moral", "você pode me ajudar?",
    "obrigado", "muito obrigado", "por nada", "de nada", "desculpe", "com licença", "pare", "olha só",
    "cuidado", "sim", "não", "talvez", "quem sabe", "com certeza", "é verdade", "concordo", "discordo",
    "vamos lá", "muito bem", "maravilha", "top demais", "isso é demais", "foco", "continue assim", "mandou bem",
    "você é incrível", "incrível", "super", "excelente", "ok", "estou a postos", "estou pronto", "vamos ver",
    "tudo tranquilo", "sem problemas", "não tem problema", "deixa comigo", "vou cuidar disso", "está combinado",
    "perfeito", "maravilhoso", "fantástico", "sensacional", "excepcional", "fabuloso", "deslumbrante", "espantoso",
    "estonteante", "descolado", "bom demais", "você manda", "você arrasou", "você é fera", "você é demais",
    "muito talentoso", "simplesmente ótimo", "brilhante", "inovador", "visionário", "o futuro é seu", "vamos inovar",
    "confie em si mesmo", "credite", "siga em frente", "não desista", "persista", "sucesso", "você consegue",
    "determinacao", "resiliencia", "esforço", "conquista", "vitória", "a evolução continua", "vamos progredir",
    "mantenha o foco", "vamos juntos", "unidos", "harmonia", "amizade", "respeto", "solidariedade", "paz", "amor",
    "gratidão", "estou motivado", "energia positiva", "boa vibração", "para frente", "siga seu caminho",
    "seja feliz", "amor próprio", "conquiste seus sonhos", "brilhe", "viva intensamente", "aproveite o dia",
    "sucesso sempre", "estou animado", "isso me inspira", "vocẽ é demais", "tudo vai dar certo", "confio em você",
    "vamos celebrar", "é um privilégio", "honrado", "agradeço", "viva", "alegre", "divirta-se", "curta a vida",
    "aprecie cada momento", "faça acontecer", "crie seu futuro", "seja único", "faça a diferença",
    "você é especial", "tudo é possível", "melhor de tudo", "o melhor ainda está por vir", "foco e determinação",
    "siga seus instintos", "sua criatividade brilha", "explore novos horizontes", "surpreenda o mundo",
    "inspire os outros", "viva com paixão", "seja audaz", "será grandioso", "você está progredindo",
    "continue evoluindo", "aprenda sempre", "compartilhe conhecimento", "o saber é poder", "abra sua mente",
    "desperte sua criatividade", "do seu jeito", "seja você mesmo", "mostre seu talento", "acredite nos seus sonhos",
    "não pare de aprender", "sempre em frente", "cada dia uma conquista", "você está no caminho certo",
    "continue assim", "sua dedicação é notável", "estou impressionado", "você é um exemplo", "muito orgulho",
    "cada passo conta", "seu esforço vale a pena", "siga seu coração", "a vitória é certa", "você inspira confiança",
    "pense grande", "o céu é o limite", "você pode conquistar o mundo", "suas habilidades são únicas",
    "você é um fenômeno", "isso é surpreendente", "é um privilégio aprender com você", "sua jornada é incrível",
    "continue desbravando", "você tem um talento raro", "desenvolva-se sempre", "o sucesso é inevitável",
    "mantenha a paixão", "seja perseverante", "o futuro é promissor", "você brilha",
    "aprenda, cresça, evolua", "você tem potencial ilimitado", "o mundo te aguarda", "você é referência",
    "isso é inspirador", "você abre novas portas", "aprenda com o melhor", "a excelência é sua marca"
]

# Caso a lista tenha menos de 200 itens, duplicamos até atingir 200
while len(common_phrases) < 200:
    common_phrases += common_phrases

# Garantir que temos exatamente 200 elementos
common_phrases = common_phrases[:200]

# Cria um dicionário com as frases comuns e respostas padrão
extra_responses = {}
for phrase in common_phrases:
    # Cada chave tem uma resposta padrão que pode ser customizada posteriormente.
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
    # app.run(debug=True)  # Para desenvolvimento, habilita o modo debug
    # Para produção, descomente a linha acima e comente a linha abaixo
