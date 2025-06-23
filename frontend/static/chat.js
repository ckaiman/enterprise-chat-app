function showToast(message) {
    const toast = document.getElementById("toast-notification");
    if (!toast) return;

    toast.textContent = message;
    toast.classList.add("show");

    // After 3 seconds, remove the show class
    setTimeout(() => { toast.classList.remove("show"); }, 3000);
}

function appendMessageToChat(message, sender) {
    const chatContainer = document.getElementById("chat-container");
    const messageElement = document.createElement("div");

    if (sender === "bot") {
        messageElement.classList.add("bot-reply"); // For blue text styling
        // The message for the bot can now contain HTML (like tables or <pre> tags)
        messageElement.innerHTML = "<strong>Bot:</strong> " + message;
    } else {
        // For user messages, we still use textContent for the message itself for security,
        // but we build the element with a bold prefix.
        const prefix = document.createElement("strong");
        prefix.textContent = "You: ";
        messageElement.appendChild(prefix);
        messageElement.appendChild(document.createTextNode(message));
    }
    chatContainer.prepend(messageElement); // Add new messages to the top
}

function sendMessage() {
    let message = document.getElementById("chatbox").value;
    let token = localStorage.getItem("token");
    const chatbox = document.getElementById("chatbox");

    chatbox.value = ''; // Clear the input box immediately after getting the value

    fetch("/chat", {
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
        if (replyContent === undefined || replyContent === null) {
            replyContent = "I'm sorry, I encountered an issue and can't provide a response right now.";
            console.error("Received an undefined or null reply from the server. Full response:", data);
        }

        if (typeof replyContent === 'object' && replyContent !== null && !String(replyContent).startsWith('<table')) {
            // Wrap the pretty-printed JSON in a styled <pre> tag to preserve formatting.
            replyContent = '<pre class="json-response">' + JSON.stringify(replyContent, null, 2) + '</pre>';
        }
        // alert("Reply: " + replyContent); // Remove alert
        appendMessageToChat(message, "user"); // Display user's message
        appendMessageToChat(replyContent, "bot"); // Display bot's reply
    })
    .catch(error => console.error("Chat failed", error));
}

// Add event listener for Enter key to send message
document.addEventListener('DOMContentLoaded', () => {
    // Check for authentication token. If not present, redirect to the login page.
    if (!localStorage.getItem("token")) {
        window.location.href = "login.html";
        return; // Stop further script execution
    } else {
        // If authenticated, load user details and set up the logout button.
        // This function is defined in auth.js
        loadUserDetailsAndWelcome();
    }

    const chatbox = document.getElementById('chatbox');
    if (chatbox) {
        chatbox.addEventListener('keydown', function(event) {
            // Send message on Enter key press, but allow new lines with Shift+Enter
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault(); // Prevents adding a new line
                sendMessage();
            }
        });

        // --- Speech Recognition ---
        const micToggle = document.getElementById('mic-toggle');
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

        if (SpeechRecognition) {
            const recognition = new SpeechRecognition();
            recognition.continuous = true; // Keep listening until stopped
            recognition.interimResults = true; // Show results as they are recognized
            recognition.lang = 'en-US'; // Explicitly set to the most widely supported language as a final attempt.

            micToggle.addEventListener('change', () => {
                if (micToggle.checked) {
                    try {
                        chatbox.placeholder = "Listening...";
                        chatbox.value = ""; // Clear any error messages
                        chatbox.style.color = 'inherit';
                        recognition.start();
                    } catch(e) {
                        console.error("Speech recognition could not be started.", e);
                        chatbox.value = "Error: Recognition already active.";
                        chatbox.style.color = 'red';
                        micToggle.checked = false;
                    }
                } else {
                    chatbox.placeholder = "Enter your request or question...";
                    recognition.stop();
                }
            });

            recognition.onresult = (event) => {
                let interim_transcript = '';
                let final_transcript = '';

                for (let i = event.resultIndex; i < event.results.length; ++i) {
                    if (event.results[i].isFinal) {
                        final_transcript += event.results[i][0].transcript;
                    } else {
                        interim_transcript += event.results[i][0].transcript;
                    }
                }
                chatbox.value = final_transcript + interim_transcript;
            };

            recognition.onerror = (event) => {
                console.error("Speech recognition error:", event.error);
                let errorMessage = `Speech Error: ${event.error}`;

                // Provide a more helpful message and permanently disable the feature if language is not supported.
                if (event.error === 'language-not-supported') {
                    errorMessage = "Voice input is not supported by your browser. This feature will now be hidden.";
                    // Permanently hide the toggle switch as it's not supported.
                    micToggle.parentElement.style.display = 'none';
                }

                showToast(errorMessage);
                micToggle.checked = false; // Turn off toggle on error
            };

            recognition.onend = () => {
                micToggle.checked = false; // Ensure toggle is off when recognition ends
                chatbox.placeholder = "Enter your request or question...";
            };
        } else {
            document.querySelector('.switch').style.display = 'none'; // Hide toggle if not supported
        }
    }
});
