const chatBody = document.getElementById("chatBody");
const userInput = document.getElementById("userInput");
const sendButton = document.getElementById("sendButton");

// Função para adicionar mensagens ao chat
function addMessage(text, sender = "bot") {
    const chatBody = document.getElementById("chatBody");
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("chat-message", sender);

    const messageContent = document.createElement("div");
    messageContent.classList.add("message-content");

    const messageText = document.createElement("p");
    messageText.classList.add("message-text");
    messageText.innerHTML = marked.parse(text); // Usar innerHTML para permitir negrito (**) ou links

    messageContent.appendChild(messageText);
    messageDiv.appendChild(messageContent);
    chatBody.appendChild(messageDiv);
    chatBody.scrollTop = chatBody.scrollHeight;
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

    let backendUrl;
    // Verifica se o host atual é localhost ou 127.0.0.1
    if (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1") {
        backendUrl = "http://127.0.0.1:5000/chat"; // URL para teste local
    } else {
        backendUrl = window.location.origin + "/chat"; // URL para o deploy (Render)
    }

    try {
        // Envia a mensagem para o backend
        const response = await fetch(backendUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ message: userMessage }),
        });

        // Verifica se a resposta da rede foi OK
        if (!response.ok) {
            throw new Error(`Erro HTTP! Status: ${response.status}`);
        }

        // Converte a resposta para JSON
        const data = await response.json();

        // --- Lógica para lidar com a 'action' do bot ---
        if (data.action === "redirect_to_youtube" && data.url) {
            // Se a ação for redirecionar para o YouTube, o bot já deu a resposta.
            // Aqui, adicionamos a resposta do bot e then redirecionamos.
            addMessage(data.response, "bot");
            setTimeout(() => {
                window.open(data.url, '_blank'); // Abre o link em uma nova aba
            }, 1500); // Dá um pequeno atraso para a mensagem aparecer antes de redirecionar
        } else if (data.action === "ask_for_youtube_redirect") {
            // Se o bot está perguntando se deseja redirecionar, adicionamos a resposta
            // O frontend não precisa fazer nada além de exibir a pergunta
            addMessage(data.response, "bot");
            // As próximas mensagens do usuário serão tratadas pelo contexto no backend
        }
        else {
            // Se não houver uma ação específica, apenas adiciona a resposta normal
            addMessage(data.response, "bot");
        }

    } catch (error) {
        console.error("Erro ao enviar mensagem ou processar resposta:", error);
        addMessage("Desculpe, ocorreu um erro ao processar sua solicitação. Por favor, tente novamente mais tarde.", "bot");
    }
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

// Referências para os novos elementos (mantidos do seu script original)
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

document.getElementById('uploadForm').onsubmit = async function(e) {
    e.preventDefault();
    // Adiciona mensagem de loading no chat
    const loadingId = "upload-loading-" + Date.now();
    addMessage('<span id="' + loadingId + '">Enviando arquivo...</span>', "bot");

    const formData = new FormData(this);
    const res = await fetch('/upload_excel', { method: 'POST', body: formData });
    const data = await res.json();

    // Remove o loading (procura a última mensagem bot com o id)
    const loadingElem = document.getElementById(loadingId);
    if (loadingElem && loadingElem.parentElement) {
        loadingElem.parentElement.parentElement.parentElement.remove();
    }

    let md = '';
    if(data.message) md += `${data.message}\n\n`;
    if(data.sheet_url) md += `[Abrir planilha no Google Sheets](${data.sheet_url})\n\n`;
    if(data.analysis) md += `${data.analysis}\n\n`;
    if(data.error) md += `**Erro:** ${data.error}\n\n`;

    addMessage(md, "bot");
};
// Upload automático ao selecionar arquivo
document.getElementById('file').onchange = function() {
    document.getElementById('uploadForm').dispatchEvent(new Event('submit'));
};
