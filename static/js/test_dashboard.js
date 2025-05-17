document.addEventListener("DOMContentLoaded", async () => {
	const login = document.getElementById("login");
	login.addEventListener("click", () => {
		window.location.href = "/login";
	});
	await loadFAQ();
	initButtonClickHandlers();
});

function appendFAQ(faq) {
	const container = document.getElementById("faq-container");
	const link = document.createElement("div");
	link.className = "button faq-item";
	link.textContent = faq;
	container.appendChild(link);
	container.appendChild(document.createElement("br"));
}

function appendError(errorText) {
	const container = document.getElementById("report-container");
	container.innerHTML = "";
	const error = document.createElement("div");
	error.textContent = errorText;
	container.appendChild(error);
}


async function loadFAQ() {
	try {
		const response = await fetch("/reload/faq");
		if (!response.ok) {
			throw new Error(`HTTP error! Status: ${response.status}`);
		}
		const data = await response.json();

		const listed_faq = document.querySelectorAll(".faq-item");
		if (data.faq && data.faq.length > 0) {
			data.faq.forEach((faq) => {
				if (
					!Array.from(listed_faq).some((item) => item.textContent === faq)
				) {
					appendFAQ(faq);
				}
			});
		} else {
			console.log("No FAQs available");
		}
	} catch (error) {
		console.log("Error loading FAQs:", error);
	}
}


function initButtonClickHandlers() {
	const report_choice = document.getElementById("report-choice");
	report_choice.addEventListener("click", () => {
		sessionStorage.setItem("faq_question", " ");
		window.location.href = `/report?report=${encodeURIComponent(
			"test_data"
		)}`;
	});
	const faqItems = document.querySelectorAll(".faq-item:not(#report-choice)");
	faqItems.forEach((item) => {
		item.addEventListener("click", () => {
			const question = item.textContent;
			sessionStorage.setItem("faq_question", question);
			window.location.href = `/report?report=${encodeURIComponent(
				"test_data"
			)}`;
		});
	});
}
