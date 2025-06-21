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
async function sendMessage() { // <-- Esta é a ÚNICA definição de sendMessage
    const userMessage = userInput.value.trim();

    if (userMessage === "") {
        return; // Se o campo de entrada estiver vazio, não faz nada
    }

    // Adiciona a mensagem do usuário ao chat
    addMessage(userMessage, "user");

    // Limpa o campo de entrada
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

    // Converte a resposta para JSON
    const data = await response.json();

    // Adiciona a resposta do bot ao chat
    addMessage(data.response, "bot");
} // <-- Certifique-se de que esta é a chave de fechamento correta para sendMessage

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

// Referências para os novos elementos
const sidebar = document.querySelector('.sidebar');
const overlay = document.getElementById('overlay');

let touchStartX = 0;
let touchEndX = 0;
const minSwipeDistance = 50; // Distância mínima para considerar um swipe

// --- Funções para controlar a sidebar ---
function openSidebar() {
    // Abre a sidebar APENAS se estiver em tela pequena
    if (window.innerWidth <= 768) {
        sidebar.classList.add('active');
        overlay.classList.add('active');
        document.body.style.overflow = 'hidden'; // Impede rolagem do body quando sidebar aberta
    }
}

function closeSidebar() {
    sidebar.classList.remove('active');
    overlay.classList.remove('active');
    document.body.style.overflow = ''; // Permite rolagem novamente
}

// --- Event Listeners para toque/swipe ---

// Detecta o início do toque
document.addEventListener('touchstart', (e) => {
    // Evita que o swipe vertical também acione o menu acidentalmente
    // Captura a posição X inicial do toque
    touchStartX = e.changedTouches[0].screenX;
}, false);

// Detecta o fim do toque
document.addEventListener('touchend', (e) => {
    // Evita que o swipe vertical também acione o menu acidentalmente
    // Captura a posição X final do toque
    touchEndX = e.changedTouches[0].screenX;
    handleGesture();
}, false);

function handleGesture() {
    // Só processa gestos em telas pequenas
    if (window.innerWidth <= 768) {
        const swipeDistance = touchEndX - touchStartX;

        // Se a sidebar está fechada E o swipe foi para a direita (positivo) e longo o suficiente
        if (swipeDistance > minSwipeDistance && !sidebar.classList.contains('active')) {
            openSidebar();
        }
        // Se a sidebar está aberta E o swipe foi para a esquerda (negativo) e longo o suficiente
        else if (swipeDistance < -minSwipeDistance && sidebar.classList.contains('active')) {
            closeSidebar();
        }
    }
}

// --- Event Listener para fechar sidebar ao clicar no overlay ---
overlay.addEventListener('click', () => {
    closeSidebar();
});

// --- Opcional: Fechar sidebar ao redimensionar a tela (se mudar de mobile para desktop) ---
window.addEventListener('resize', () => {
    if (window.innerWidth > 768 && sidebar.classList.contains('active')) {
        closeSidebar();
    }
});