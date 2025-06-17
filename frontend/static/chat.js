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
    .then(data => alert("Reply: " + data.reply))
    .catch(error => console.error("Chat failed", error));
}