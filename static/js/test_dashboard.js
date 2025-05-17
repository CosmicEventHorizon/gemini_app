document.addEventListener("DOMContentLoaded", () => {
	const login = document.getElementById("login");

	login.addEventListener("click", () => {
		window.location.href = "/login";
	});

	//poll reports
	function reloadStatus() {
		fetch("/reload/faq")
			.then((response) => {
				if (!response.ok)
					throw new Error(`HTTP error! Status: ${response.status}`);
				return response.json();
			})
			.then((data) => {
				const listed_faq = document.querySelectorAll(".faq-item");
				if (data.faq && data.faq.length > 0) {
					data.faq.forEach((faq) => {
						if (
							!Array.from(listed_faq).some((item) => item.textContent === faq)
						) {
							appendFAQ(faq);
						}
					});
					initFAQClickHandlers();
				} else {
					console.log("No reports available");
				}
			})
			.catch((error) => {
				console.log("Error loading reports");
			})
			.finally(() => {
				setTimeout(reloadStatus, 10000);
			});
	}
	reloadStatus();

	//choose report
	const report_choice = document.getElementById("report-choice");
	report_choice.addEventListener("click", () => {
		window.location.href = `/report?report=${encodeURIComponent("test_data")}`;
	});
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

function initFAQClickHandlers() {
	const faqItems = document.querySelectorAll(".faq-item");

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
