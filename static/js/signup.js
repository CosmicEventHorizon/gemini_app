document.addEventListener("DOMContentLoaded", function () {
	const signupForm = document.querySelector("form");

	signupForm.addEventListener("submit", function (event) {
		event.preventDefault(); 

		const formData = new FormData(signupForm);

		fetch("/signup", {
			method: "POST",
			body: formData,
		})
			.then((response) => {
				if (response.status === 201) {
					alert("Signup successful! You can login now");
                    window.location.href = "/login";
				} else {
					alert("Signup failed. Please try again.");
				}
			})
			.catch((error) => {
				console.error("Error during signup:", error);
				alert("An error occurred. Please try again later.");
			});
	});
});
