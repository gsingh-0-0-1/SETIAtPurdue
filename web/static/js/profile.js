async function loadInfo() {
        var response = await fetch("/whoami", {
                method: "GET",
        })
        .then((response) => {
                if (response.status == 200) {
                        return response.json()
                }
        })
        .then((jsondata) => {
        	document.getElementById("displayname").textContent = jsondata["fullname"]
		document.getElementById("username").textContent = jsondata["user"]
		document.getElementById("email").textContent = jsondata["email"]
		document.getElementById("affil").textContent = jsondata["affil"]
	})
}

loadInfo()
