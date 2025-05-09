document.addEventListener("DOMContentLoaded", () => {
	const form = document.getElementById("chat-form");
	const input = document.getElementById("chat-input");
	const container = document.getElementById("chat-container");
	const load_notification = document.getElementById("load-notification")


	form.addEventListener("submit", async (e) => {
		e.preventDefault();
		const prompt = input.value;
		if (!prompt) return;

		appendMessage("user", prompt);
		input.value = "";

		appendMessage("bot", "...");
		const loadingElement = container.lastElementChild;

		try {
			const res = await fetch("/product", {
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
		const div = document.createElement("div");
		div.className = `message ${sender}`;
		const formattedHtml = marked.parse(text);
		div.innerHTML = formattedHtml;
		container.appendChild(div);
		container.scrollTop = container.scrollHeight;
	}

	function checkStatus() {
		fetch('/reload/status')
			.then(res => res.json())
			.then(data => {
				if (data.done) {
					load_notification.innerText = 'Database Loaded';
				} else {
					setTimeout(checkStatus, 2000);  
				}
			});
	}
	
	checkStatus();

});
