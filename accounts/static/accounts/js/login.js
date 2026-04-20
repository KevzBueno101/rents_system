// Generic toggle password function
function togglePassword(targetId, iconId) {
    const pass = document.getElementById(targetId);
    const icon = document.getElementById(iconId);
    if (pass && icon) {
        if (pass.type === "password") {
            pass.type = "text";
            icon.classList.replace("bi-eye", "bi-eye-slash");
        } else {
            pass.type = "password";
            icon.classList.replace("bi-eye-slash", "bi-eye");
        }
    }
}

// Role toggle function
function selectRole(role) {
    document.getElementById("roleInput").value = role;
    const btnAdmin = document.getElementById("btnAdmin");
    const btnTenant = document.getElementById("btnTenant");
    const signupSection = document.getElementById("signupSection");

    if (role === "admin") {
        btnAdmin.classList.add("active");
        btnTenant.classList.remove("active");
        signupSection.classList.add("d-none");
    } else {
        btnTenant.classList.add("active");
        btnAdmin.classList.remove("active");
        signupSection.classList.remove("d-none");
    }
}

// Initialization function to attach event listeners
function initLoginPage() {
    // Attach role button listeners
    document.getElementById("btnAdmin").addEventListener("click", () => selectRole("admin"));
    document.getElementById("btnTenant").addEventListener("click", () => selectRole("tenant"));

    // Attach password toggle listeners
    document.querySelectorAll(".toggle-password").forEach(span => {
        span.addEventListener("click", function() {
            const targetId = this.dataset.target || "password"; // Default to "password", or use data-target
            const iconId = this.querySelector("i").id;
            togglePassword(targetId, iconId);
        });
    });
}

// Run init on DOM load
document.addEventListener("DOMContentLoaded", initLoginPage);