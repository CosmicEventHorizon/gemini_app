document.addEventListener("DOMContentLoaded", () => {
	//get variables to be used for the request
	const urlParams = new URLSearchParams(window.location.search);
	const report_name = urlParams.get("report");
	const report = report_name || sessionStorage.getItem("report");
	if (report_name) {
		sessionStorage.setItem("report", report_name);
	}
	const faq_question = sessionStorage.getItem("faq_question") || null;
	if (faq_question != " ") {
		appendMessage("user", faq_question);
		sendPrompt(faq_question, report);
	}

	//get html elements
	const form = document.getElementById("chat-form");
	const input = document.getElementById("chat-input");
	const load_notification = document.getElementById("load-notification");

	form.addEventListener("submit", async (e) => {
		e.preventDefault();
		const prompt = input.value;
		if (!prompt) return;

		appendMessage("user", prompt);
		input.value = "";
		sendPrompt(prompt, report);
	});

	load_notification.innerText = report;
});

function appendMessage(sender, text) {
	const container = document.getElementById("chat-container");
	const div = document.createElement("div");
	div.className = `message ${sender}`;
	const formattedHtml = marked.parse(text);
	div.innerHTML = formattedHtml;
	container.appendChild(div);
	container.scrollTop = container.scrollHeight;
}

async function sendPrompt(prompt, report) {
	const container = document.getElementById("chat-container");
	appendMessage("bot", "...");
	const loadingElement = container.lastElementChild;

	try {
		const res = await fetch("/report", {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ prompt, report }),
		});
		const data = await res.json();
		loadingElement.remove();
		appendMessage("bot", data.response || "No response.");
	} catch (err) {
		loadingElement.remove();
		appendMessage("bot", "Error contacting server.");
	}
}
