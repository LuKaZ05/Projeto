function submitForm() {
    const formData = {
        name: document.getElementById("name").value,
        email: document.getElementById("email").value,
        password: document.getElementById("password").value,
        confirm_password: document.getElementById("confirm_password").value,
        role: document.getElementById("role").value,
        crm: document.getElementById("crm").value || null,
        crbm: document.getElementById("crbm").value || null
    };

    if (formData.password !== formData.confirm_password) {
        alert("As senhas não coincidem!");
        return;
    }

    fetch("/register", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(formData)
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
            } else {
                alert(data.message);
                window.location.href = "/login"; // Redirecionar para a página de login
            }
        })
        .catch(error => console.error("Erro:", error));
}
