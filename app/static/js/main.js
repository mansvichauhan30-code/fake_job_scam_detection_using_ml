/* ============================================================
   Fake Job Scam Detection System - Main JS
   ============================================================ */

document.addEventListener("DOMContentLoaded", function () {

    // Auto-dismiss flash messages after 5 seconds
    const alerts = document.querySelectorAll(".alert");
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 5000);
    });

    // Client-side password confirmation check on registration form
    const confirmPassword = document.getElementById("confirm_password");
    const password = document.getElementById("password");

    if (confirmPassword && password) {
        const form = confirmPassword.closest("form");
        form.addEventListener("submit", function (e) {
            if (password.value !== confirmPassword.value) {
                e.preventDefault();
                alert("Passwords do not match. Please re-check.");
                confirmPassword.focus();
            }
        });
    }

    // Simple character counter for job description textarea (analyze page)
    const description = document.getElementById("description");
    if (description) {
        const counter = document.createElement("div");
        counter.className = "form-text text-end";
        description.parentNode.appendChild(counter);

        const updateCounter = () => {
            counter.textContent = `${description.value.length} characters`;
        };
        description.addEventListener("input", updateCounter);
        updateCounter();
    }

});
