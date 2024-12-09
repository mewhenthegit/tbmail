document.getElementById("link").addEventListener("click", async (ev)=>{
    if (document.getElementById("password").value.length == 0 || document.getElementById("address").value.length == 0) {
        alert("Please fill in all fields!");
        return;
    }

    let resp = await fetch("http://127.0.0.1:8000/api/recover/submit", {
        method: "POST",
        body: JSON.stringify({
            "address": document.getElementById("address").value,
            "password": document.getElementById("password").value
        })
    });

    if (resp.status != 200) {
        alert("Something went wrong!");
        return;
    }

    let body = await resp.json();

    if (body.success == false) {
        document.getElementById("password").value = ""
        document.getElementById("address").value = ""
        alert(body.error);
        return
    }

    document.getElementById("Linking area").innerHTML = `Log onto Trollbox and use the ?recover command to link your account<br>Your code is: <br><h3>${body.code}</h3>`
});