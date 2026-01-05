const API_URL = "http://localhost:8000/chat"; // FastAPI URL


function addMessage(text, sender) {
    const messagesDiv = document.getElementById("messages");
    const messageDiv = document.createElement("div");

    messageDiv.className = sender;
    messageDiv.innerText = text;

    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

async function sendMessage() {
    const input = document.getElementById("messageInput");
    const message = input.value.trim();

    if (message === "") return;

    // Show user message
    addMessage(message, "user");
    input.value = "";

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: message
            })
        });

        const data = await response.json();

        // Show bot reply
        addMessage(data.reply, "bot");

    } catch (error) {
        addMessage("Error connecting to server.", "bot");
        console.error(error);
    }
}
