document.addEventListener("DOMContentLoaded", () => {
	//reload database
	/*
    const reload = document.getElementById("reload-database");
	reload.addEventListener("click", async (e) => {
		e.preventDefault();
		try {
			const res = await fetch("/reload", {
				method: "POST",
			});
			if (res.status === 204) {
				alert("Database reloaded");
			} else {
				alert("Error reloading database");
			}
		} catch (e) {
                alert("Server error")
        }
	});
    */
   
	//report bot
	const form = document.getElementById("chat-form");
	const input = document.getElementById("chat-input");
	const container = document.getElementById("chat-container");

	form.addEventListener("submit", async (e) => {
		e.preventDefault();
		const prompt = input.value;
		if (!prompt) return;

		appendMessage("user", prompt);
		input.value = "";

		appendMessage("bot", "..."); 
		const loadingElement = container.lastElementChild;

		try {
			const res = await fetch("/report", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ prompt }),
			});
			const data = await res.json();
			loadingElement.remove(); 
			appendMessage("bot", data.response || "No response.");
		} catch (err) {
			loadingElement.remove();
			appendMessage("bot", "Error contacting server.");
		}
	});

	function appendMessage(sender, text) {
		const div = document.createElement("pre");
		div.className = `message ${sender}`;
		div.textContent = text;
		container.appendChild(div);
		container.scrollTop = container.scrollHeight;
	}
});
