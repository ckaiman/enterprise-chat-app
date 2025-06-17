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
        let replyContent = data.reply;
        if (typeof replyContent === 'object' && replyContent !== null) {
            replyContent = JSON.stringify(replyContent, null, 2); // Pretty print JSON
        }
        alert("Reply: " + replyContent);
    })
    .catch(error => console.error("Chat failed", error));
}