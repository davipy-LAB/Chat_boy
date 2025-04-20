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

    // Rolagem automática para a última mensagem
    chatBody.scrollTop = chatBody.scrollHeight;
}

// Função para enviar a mensagem do usuário
function sendMessage() {
    const message = userInput.value.trim();
    if (message === "") return;

    addMessage(message, "user"); // Adiciona a mensagem do usuário
    userInput.value = ""; // Limpa o campo de input

    fetch("http://127.0.0.1:5000/chat", { // 🔥 Porta corrigida para 5000
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ message }),
    })
        .then((response) => response.json())
        .then((data) => {
            addMessage(data.response, "bot"); // Adiciona a resposta da IA
        })
        .catch((error) => {
            console.error("Erro ao enviar mensagem:", error);
        });
}

// Evento de clique no botão de enviar
sendButton.addEventListener("click", sendMessage);

// Evento de tecla pressionada no campo de input
userInput.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
        event.preventDefault(); // 🔥 Impede o recarregamento da página
        sendMessage();
    }
});