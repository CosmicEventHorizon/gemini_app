document.addEventListener("DOMContentLoaded", async () => {
	const logout = document.getElementById("logout");
	//logout logic
	logout.addEventListener("click", () => {
		fetch("/logout", {
			method: "POST",
		}).then((response) => {
			if (response.ok) {
				window.location.href = "/";
			}
		});
	});

	//add report to database
	const report_form = document.getElementById("report-form");
	report_form.addEventListener("submit", function (e) {
		e.preventDefault();
		submitReport();
	});

	//poll reports
	function reloadReports() {
		fetch("/reload/report")
			.then((response) => {
				if (!response.ok)
					throw new Error(`HTTP error! Status: ${response.status}`);
				return response.json();
			})
			.then((data) => {
				const listed_reports = document.querySelectorAll(".report-item");
				if (data.reports && data.reports.length > 0) {
					data.reports.forEach((report) => {
						if (
							!Array.from(listed_reports).some(
								(item) => item.textContent === report
							)
						) {
							appendReport(report);
						}
					});
					initReportClickHandlers();
				} else {
					appendError("No reports available");
				}
			})
			.catch((error) => {
				appendError("Error loading reports");
			})
			.finally(() => {
				setTimeout(reloadReports, 10000);
			});
	}
	reloadReports();
	await loadFAQ();
	initButtonClickHandlers();
});

function appendReport(report_name) {
	const container = document.getElementById("report-container");
	const link = document.createElement("div");
	link.className = "button report-item";
	link.textContent = report_name;
	container.appendChild(link);
	container.appendChild(document.createElement("br"));
}

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

function submitReport() {
	const formData = new FormData(document.getElementById("report-form"));

	fetch("/add-report", {
		method: "POST",
		body: formData,
	})
		.then((response) => {
			if (!response.ok) {
				return response.json().then((err) => {
					throw err;
				});
			}
			return response.json();
		})
		.then((data) => {
			alert(data.message);
		})
		.catch((error) => {
			if (error.message) {
				alert(error.message);
			} else {
				alert("An error occurred while submitting the report.");
			}
		});
}

function initReportClickHandlers() {
	const reports = document.querySelectorAll(".report-item");
	reports.forEach((report) => {
		report.addEventListener("click", () => {
			reports.forEach((r) => {
				r.classList.remove("report-selected");
			});
			report.classList.add("report-selected");
		});
	});
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
		const selected_report = document.getElementsByClassName("report-selected");
		if (selected_report.length === 0) {
			alert("Please choose a report!");
			return;
		}
		sessionStorage.setItem("faq_question", " ");
		window.location.href = `/report?report=${encodeURIComponent(
			selected_report[0].textContent
		)}`;
	});
	const faqItems = document.querySelectorAll(".faq-item:not(#report-choice)");
	faqItems.forEach((item) => {
		item.addEventListener("click", () => {
			const question = item.textContent;
			const selected_report =
				document.getElementsByClassName("report-selected");
			if (selected_report.length === 0) {
				alert("Please choose a report!");
				return;
			}
			sessionStorage.setItem("faq_question", question);
			window.location.href = `/report?report=${encodeURIComponent(
				selected_report[0].textContent
			)}`;
		});
	});
}
