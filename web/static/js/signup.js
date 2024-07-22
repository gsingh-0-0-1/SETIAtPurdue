async function fetchAffils() {
	var response = await fetch("/all_affils", {
                method: "GET",
        })
        .then((response) => {
		if (response.status == 200) {
			return response.json()
		}
	})
	.then((jsondata) => {
		var data = jsondata["data"]
		var options = document.getElementById("user_input_affiliation")
		for (var key in data) {
			var affil = data[key]
			options.innerHTML += '<option value="' + affil + '">' + affil + '</option>'
		}
        })
}

function checkPasswordMatch() {
	var password = document.getElementById('user_input_password').value;
	var confirmPassword = document.getElementById('user_input_password-confirm').value;
	var message = document.getElementById('error_message');

	if (password === confirmPassword) {
		message.textContent = ""
		document.getElementById('user_input_password-confirm').classList.remove('mismatch');
		document.getElementById('user_input_password-confirm').classList.add('match');
		document.getElementById("submit-button").disabled = false;
	} else {
		message.textContent = 'Passwords do not match.';
		document.getElementById('user_input_password-confirm').classList.remove('match');
		document.getElementById('user_input_password-confirm').classList.add('mismatch');
		document.getElementById("submit-button").disabled = true;
	}
}

document.getElementById('user_input_password-confirm').addEventListener('input', checkPasswordMatch);

fetchAffils()
