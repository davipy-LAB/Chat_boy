const chatBody = document.getElementById("chatBody");
const userInput = document.getElementById("userInput");
const sendButton = document.getElementById("sendButton");

// Função para adicionar mensagens ao chat
function addMessage(text, sender) {
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("chat-message", sender);

    const messageContent = document.createElement("div");
    messageContent.classList.add("message-content");

    const messageText = document.createElement("p");
    messageText.classList.add("message-text");
    messageText.textContent = text;

    messageContent.appendChild(messageText);
    messageDiv.appendChild(messageContent);
    chatBody.appendChild(messageDiv);

    chatBody.scrollTop = chatBody.scrollHeight; // Rolagem automática para a última mensagem
}

// Função para enviar a mensagem para o backend e obter a resposta
async function sendMessage() {
    const userMessage = userInput.value.trim();

    if (userMessage === "") {
        return; // Se o campo de entrada estiver vazio, não faz nada
    }

    // Adiciona a mensagem do usuário ao chat
    addMessage(userMessage, "user");

    // Limpa o campo de entrada
    userInput.value = "";

// Função para enviar a mensagem para o backend e obter a resposta
async function sendMessage() {
    const userMessage = userInput.value.trim();

    if (userMessage === "") {
        return;
    }

    addMessage(userMessage, "user");
    userInput.value = "";

    let backendUrl;
    // Verifica se o host atual é localhost ou 127.0.0.1
    if (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1") {
        backendUrl = "http://127.0.0.1:5000/chat"; // URL para teste local
    } else {
        backendUrl = window.location.origin + "/chat"; // URL para o deploy (Render)
    }

    // Envia a mensagem para o backend
    const response = await fetch(backendUrl, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: userMessage }),
    });

    const data = await response.json();
    addMessage(data.response, "bot");
}

// ... (restante do seu código JS) ...

    // Converte a resposta para JSON
    const data = await response.json();

    // Adiciona a resposta do bot ao chat
    addMessage(data.response, "bot");
}

// Função que ativa o envio ao pressionar Enter
userInput.addEventListener("keypress", (event) => {
    if (event.key === "Enter") {
        sendMessage();
    }
});

// Adiciona o evento de clique no botão de enviar
sendButton.addEventListener("click", () => {
    sendMessage();
});
