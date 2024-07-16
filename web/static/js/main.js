async function storeJWT(response) {
	var body = await response.json()
	localStorage.setItem("SETICitizenJWT", body["jwt"])	
}

async function handleUserSignup() {
	var response = await fetch("/signup_request", {
		headers: {
			"Content-Type": "application/json",
		},
		method: "POST",
		body: JSON.stringify({
			username: document.getElementById("user_input_username").value,
			password: document.getElementById("user_input_password").value
		})
	})
	storeJWT(response)
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
	storeJWT(response)
}

