function appendMessageToChat(message, sender) {
    const chatContainer = document.getElementById("chat-container");
    const messageElement = document.createElement("div");
    messageElement.textContent = message;
    if (sender === "bot") {
        messageElement.classList.add("bot-reply"); // For blue text styling
    }
    chatContainer.appendChild(messageElement);
    chatContainer.scrollTop = chatContainer.scrollHeight; // Scroll to the bottom
}

function sendMessage() {
    let message = document.getElementById("chatbox").value;
    let token = localStorage.getItem("token");

    fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        body: JSON.stringify({message})
    })
    .then(response => response.json())
    .then(data => {
        // Log to see what data.reply actually is
        console.log("Received data from /chat endpoint:", data);
        console.log("Type of data.reply:", typeof data.reply);
        console.log("Value of data.reply:", data.reply);
        let replyContent = data.reply;
        if (typeof replyContent === 'object' && replyContent !== null) {
            replyContent = JSON.stringify(replyContent, null, 2); // Pretty print JSON
        }
        // alert("Reply: " + replyContent); // Remove alert
        appendMessageToChat("You: " + message, "user"); // Display user's message
        appendMessageToChat("Bot: " + replyContent, "bot"); // Display bot's reply
    })
    .catch(error => console.error("Chat failed", error));
}