document.getElementById("link").addEventListener("click", async (ev)=>{
    if (document.getElementById("password").value.length == 0) {
        alert("Please fill in a password!");
        return;
    }

    let resp = await fetch("http://tbmail.codersquack.nl/api/link/submit", {
        method: "POST",
        body: JSON.stringify({"password": document.getElementById("password").value})
    });

    if (resp.status != 200) {
        alert("Something went wrong!");
        return;
    }

    let body = await resp.json();

    document.getElementById("Linking area").innerHTML = `Log onto Trollbox and use the ?link command to link your account<br>Your code is: <br><h3>${body.code}</h3>`
});