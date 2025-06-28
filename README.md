# 🤖 ChatBoy — Assistente Virtual Autoral

> *Versão atual:* v1.6.1V  
> Criado por *Davi*, desenvolvedor de 16 anos com 4 anos de experiência em programação.

O *ChatBoy* é uma assistente virtual desenvolvida 100% do zero, com uma *engine autoral* baseada em *Flask, **Flask-CORS* e *random*. Sem utilizar modelos de IA prontos, ele traz funcionalidades práticas e uma estrutura modular, focada em experiências reais de uso.

![FOTO MENU](https://github.com/user-attachments/assets/0d2d6752-00d1-4099-af3f-1afbd113a248)



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

![FOTO API CLIMA](https://github.com/user-attachments/assets/64c21059-cbfc-4fd3-bd8e-f26e7b4bb3e5)



---

### ✅ 2. Verificação de vídeos no YouTube (YouTube Data API)
- Detecta perguntas como:  
  "Lançou vídeo novo de CanalTal?"
- Retorna o vídeo mais recente do canal especificado.
- Pergunta ao usuário se deseja ser redirecionado.
- Funciona em dispositivos móveis e PC.

![image](https://github.com/user-attachments/assets/8828e06c-00b7-4fb0-b0c0-f155e17693d1)



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

![image](https://github.com/user-attachments/assets/11739985-1a2c-4e2e-a34d-5608e5626519)

---

### 🔬 4. Análise de arquivos CSV (em desenvolvimento)
- Upload e leitura de arquivos .csv.
- Leitura e interpretação dos dados para análise automatizada.
- Atualmente em fase experimental.

---

### 🕹 5. Compatibilidade universal

O ChatBoy é leve e altamente otimizado, rodando até mesmo em navegadores com suporte limitado:

✅ PCs e notebooks (qualquer sistema)

✅ Dispositivos móveis (Android, iOS)

✅ Navegadores de Smart TVs

✅ PlayStation 4 (confirmado via navegador do console!)


> 🧪 Testado com sucesso no navegador do PS4, com todas as funções principais operando corretamente, inclusive as APIs de clima, YouTube e pesquisa.

![NAVEGADOR PS4 - MODO JANELA](https://github.com/user-attachments/assets/6022fd8d-54e3-47b8-ab03-6798d243d42a)

![NAVEGADOR PS4 - TELA CHEIA](https://github.com/user-attachments/assets/64c73f0e-bfb9-4fcd-a15f-6ecbe53327c9)



---

## 🚀 Atualizações frequentes

- ✅ *+75 commits no Git*
- ✅ *+65 deploys realizados*
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
