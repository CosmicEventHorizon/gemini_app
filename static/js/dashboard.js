document.addEventListener("DOMContentLoaded", () => {
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
	function reloadStatus() {
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
				setTimeout(reloadStatus, 10000);
			});

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
							!Array.from(listed_faq).some(
								(item) => item.textContent === faq
							)
						) {
							appendFAQ(faq);
						}
					});
					//initFAQClickHandlers();
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
		const selected_report = document.getElementsByClassName("report-selected");
		if (selected_report.length === 0) {
			alert("Please choose a report!");
			return;
		}
		window.location.href = `/report?report=${encodeURIComponent(
			selected_report[0].textContent
		)}`;
	});
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

function initFAQClickHandlers() {
	const faqItems = document.querySelectorAll(".faq-item");

	faqItems.forEach((item) => {
		item.addEventListener("click", () => {
			const question = item.textContent;

			sessionStorage.setItem("faq_question", question);

			window.location.href = "/report";
		});
	});
}