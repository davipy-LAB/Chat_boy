import spacy
import random


nlp = spacy.load("pt_core_news_sm")

# Definir padrões de resposta
respostas = {
    "saudacao": ["Olá! Como posso ajudar?", "Oi! Tudo bem?", "Olá, como posso te ajudar hoje?"],
    "despedida": ["Até logo!", "Tchau! Foi bom conversar com você!", "Até mais!"],
    "nome": ["Sou um chatbot criado para ajudar você!", "Me chamo ChatGuy!"]
}

# Função para identificar a intenção do usuário
def identificar_intencao(mensagem):
    mensagem = mensagem.lower()
    
    if any(palavra in mensagem for palavra in ["oi", "olá", "e aí"]):
        return "saudacao"
    elif any(palavra in mensagem for palavra in ["tchau", "adeus", "até logo"]):
        return "despedida"
    elif any(palavra in mensagem for palavra in ["qual seu nome", "quem é você"]):
        return "nome"
    
    return "desconhecido"

# Função para responder ao usuário
def responder(mensagem):
    intencao = identificar_intencao(mensagem)
    if intencao in respostas:
        return random.choice(respostas[intencao])
    else:
        return "Desculpe, eu não entendi. Pode me perguntar outra coisa?"

print(responder("Oi, tudo bem?"))