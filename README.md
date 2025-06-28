# 🤖 ChatBoy — Assistente Virtual Autoral

> *Versão atual:* v1.6.1V  
> Criado por *Davi*, desenvolvedor de 16 anos com 4 anos de experiência em programação.

O *ChatBoy* é uma assistente virtual desenvolvida 100% do zero, com uma *engine autoral* baseada em *Flask, **Flask-CORS* e *random*. Sem utilizar modelos de IA prontos, ele traz funcionalidades práticas e uma estrutura modular, focada em experiências reais de uso.

![Imagem do WhatsApp de 2025-06-28 à(s) 08 31 33_44f3f61b](https://github.com/user-attachments/assets/7e59f187-674e-4b71-a04f-c636211110db)


---

## 🧠 Como funciona o ChatBoy?

O ChatBoy foi projetado com um sistema próprio de *Processamento de Linguagem Natural* (NLP). Embora não tenha a complexidade de modelos como o GPT-4o, ele é baseado em *contexto*, através das funções context() e get_response().

Por exemplo:  
Se context() identificar a trigger "quando vai", ele ativa o get_response() e chama a *API necessária* com base na intenção da pergunta do usuário.



---

## ⚙ Funcionalidades

### ✅ 1. Clima em tempo real (OpenWeatherMap)
- Detecção automática de perguntas relacionadas ao clima.
- Integração com a *API do OpenWeatherMap*.
- Retorna temperatura, sensação térmica e condições do local (padrão: Rio de Janeiro, mas aceita qualquer cidade).

*Exemplo:*  
> "Qual é o clima da Alemanha agora?"  
> → "O clima atual da Alemanha é de 14°C com sensação térmica de 12°C."

---

### ✅ 2. Verificação de vídeos no YouTube (YouTube Data API)
- Detecta perguntas como:  
  "Lançou vídeo novo de CanalTal?"
- Retorna o vídeo mais recente do canal especificado.
- Pergunta ao usuário se deseja ser redirecionado.
- Funciona em dispositivos móveis e PC.

---

### ✅ 3. Pesquisa no Google (Google Custom Search API)
- Permite buscas em tempo real sobre:
  - Saúde
  - Política
  - Esportes
  - Séries e filmes
  - Jogos
  - Educação
  - Notícias em geral

Essa funcionalidade torna o ChatBoy *extremamente útil no dia a dia*, mantendo o foco em entretenimento e informação.

---

### 🔬 4. Análise de arquivos CSV (em desenvolvimento)
- Upload e leitura de arquivos .csv.
- Leitura e interpretação dos dados para análise automatizada.
- Atualmente em fase experimental.

---

## 🚀 Atualizações frequentes

- ✅ *+59 commits no Git*
- ✅ *+50 deploys realizados*
- 🗓 Projeto iniciado em *abril de 2025*.
- Atualizações constantes com novos recursos e melhorias.

---

## 🔗 Teste o ChatBoy

Acesse agora a *versão base online*:

👉 [https://chatboy-el6y.onrender.com/](https://chatboy-el6y.onrender.com/)

---

## 👨‍💻 Sobre o criador

*Davi*, 16 anos, programador autodidata com experiência em:
- HTML, CSS, JavaScript
- React.js, Node.js, Express
- Python, Django, Flask
- Flask (utilizado no ChatBoy)
- UX, UI
- GML
- NLP, ML (Machine Learning)

O ChatBoy representa seu projeto mais ambicioso até agora, com toda a lógica e estrutura *desenvolvidas 100% manualmente*.

---

📫 Entre em contato, contribua ou confira outros projetos no portfólio
Contato: https://www.linkedin.com/in/davi-dias-de-souza-5337872a6/
Chave pix para apoio financeiro: chatboy0800@gmail.com
