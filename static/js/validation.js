(function () {
  "use strict";

  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  function scorePassword(value) {
    let score = 0;
    if (value.length >= 8) score += 25;
    if (/[a-z]/.test(value)) score += 20;
    if (/[A-Z]/.test(value)) score += 20;
    if (/\d/.test(value)) score += 15;
    if (/[^A-Za-z0-9]/.test(value)) score += 20;
    return Math.min(score, 100);
  }

  function updateStrength(input) {
    const meter = document.querySelector(".strength-meter span");
    const text = document.getElementById("strengthText");
    if (!meter || !text) return;

    const score = scorePassword(input.value);
    meter.style.width = `${score}%`;

    if (score < 45) {
      meter.style.background = "var(--danger)";
      text.textContent = "Password is weak. Add uppercase, number, and symbol.";
    } else if (score < 75) {
      meter.style.background = "var(--warning)";
      text.textContent = "Password is improving. Add one more character type.";
    } else {
      meter.style.background = "var(--accent)";
      text.textContent = "Strong password. Nice and backend-ready.";
    }
  }

  function validateField(field) {
    if (field.type === "email" && field.value && !emailPattern.test(field.value)) {
      field.setCustomValidity("Invalid email");
    } else if (field.dataset.match) {
      const source = document.getElementById(field.dataset.match);
      field.setCustomValidity(source && field.value !== source.value ? "Passwords do not match" : "");
    } else {
      field.setCustomValidity("");
    }

    const isValid = field.checkValidity();
    field.classList.toggle("is-invalid", !isValid);
    field.classList.toggle("is-valid", isValid && field.value.length > 0);
    return isValid;
  }

  function showToast(message) {
    const toastEl = document.getElementById("appToast");
    if (!toastEl || !window.bootstrap) return;
    toastEl.querySelector(".toast-body").textContent = message;
    new bootstrap.Toast(toastEl).show();
  }

  document.querySelectorAll("[data-password-strength]").forEach((input) => {
    input.addEventListener("input", () => updateStrength(input));
  });

  document.querySelectorAll(".js-validate").forEach((form) => {
    const fields = form.querySelectorAll("input, textarea, select");

    fields.forEach((field) => {
      field.addEventListener("input", () => validateField(field));
      field.addEventListener("blur", () => validateField(field));
    });

    form.addEventListener("submit", (event) => {
      event.preventDefault();
      let valid = true;
      fields.forEach((field) => {
        if (!validateField(field)) valid = false;
      });

      form.classList.add("was-validated");
      if (!valid) return;

      const success = form.parentElement.querySelector(".form-success");
      if (success) success.classList.remove("d-none");

      const signupSuccess = document.getElementById("signupSuccess");
      if (signupSuccess && form.id === "signupForm") {
        signupSuccess.classList.add("is-visible");
      }

      showToast("Form validated successfully. Ready for Django backend.");
      form.reset();
      fields.forEach((field) => field.classList.remove("is-valid", "is-invalid"));
    });
  });

  window.LearnSphereValidation = { validateField, scorePassword };
})();
