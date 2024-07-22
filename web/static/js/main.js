async function handleUserSignup() {
	var response = await fetch("/signup_request", {
		headers: {
			"Content-Type": "application/json",
		},
		method: "POST",
		body: JSON.stringify({
			username: document.getElementById("user_input_username").value,
			password: document.getElementById("user_input_password").value,
			fullname: document.getElementById("user_input_fullname").value,
			email: document.getElementById("user_input_email").value,
			affil: document.getElementById("user_input_affiliation").value
		})
	})
	.then((response) => {
                if (response.status == 200) {
                        window.location.href = "/profile"
                }
		else {
			return response.text()
		}
        })
	.then((text) => {
                document.getElementById("error_message").textContent = text
        })
}

async function handleUserLogin() {
	var response = await fetch("/login_request", {
                headers: {
                        "Content-Type": "application/json",
			"Authorization": "Bearer " + localStorage.getItem("SETICitizenJWT")
                },
                method: "POST",
                body: JSON.stringify({
                        username: document.getElementById("user_input_username").value,
                        password: document.getElementById("user_input_password").value
                })
        })
	.then((response) => {
		if (response.status == 200) {
			window.location.href = "/profile"
		}
		else {
			return response.text()
		}
	})
	.then((text) => {
		document.getElementById("error_message").textContent = text
	})
}

document.addEventListener("keypress", function(event) {
	if (event.key === "Enter") {
		event.preventDefault();
		document.getElementById("submit-button").click();
	}
});
