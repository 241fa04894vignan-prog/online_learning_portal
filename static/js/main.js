(function () {
  "use strict";

  const root = document.documentElement;
  const navbar = document.getElementById("siteNavbar");
  const backToTop = document.getElementById("backToTop");
  const themeToggle = document.getElementById("themeToggle");
  const loader = document.getElementById("pageLoader");

  function setTheme(theme) {
    root.setAttribute("data-theme", theme);
    localStorage.setItem("learnsphere-theme", theme);
    if (themeToggle) {
      themeToggle.innerHTML = theme === "dark" ? '<i class="fa-solid fa-sun"></i>' : '<i class="fa-solid fa-moon"></i>';
    }
  }

  function handleScroll() {
    const scrolled = window.scrollY > 20;
    if (navbar) navbar.classList.toggle("nav-scrolled", scrolled);
    if (backToTop) backToTop.classList.toggle("is-visible", window.scrollY > 420);
  }

  function animateCounters() {
    const counters = document.querySelectorAll("[data-counter]");
    if (!counters.length) return;

    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        const counter = entry.target;
        const target = Number(counter.dataset.counter);
        const duration = 1400;
        const startTime = performance.now();

        function tick(now) {
          const progress = Math.min((now - startTime) / duration, 1);
          const value = Math.floor(progress * target);
          counter.textContent = value >= 1000 ? `${Math.floor(value / 1000)}k+` : value;
          if (progress < 1) requestAnimationFrame(tick);
          else counter.textContent = target >= 1000 ? `${Math.floor(target / 1000)}k+` : `${target}+`;
        }

        requestAnimationFrame(tick);
        observer.unobserve(counter);
      });
    }, { threshold: .5 });

    counters.forEach((counter) => observer.observe(counter));
  }

  function initRippleButtons() {
    document.querySelectorAll(".ripple-btn").forEach((button) => {
      button.addEventListener("click", (event) => {
        const ripple = document.createElement("span");
        const rect = button.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        ripple.className = "ripple";
        ripple.style.width = `${size}px`;
        ripple.style.height = `${size}px`;
        ripple.style.left = `${event.clientX - rect.left - size / 2}px`;
        ripple.style.top = `${event.clientY - rect.top - size / 2}px`;
        button.appendChild(ripple);
        setTimeout(() => ripple.remove(), 650);
      });
    });
  }

  function initPasswordToggles() {
    document.querySelectorAll(".toggle-password").forEach((button) => {
      button.addEventListener("click", () => {
        const input = document.getElementById(button.dataset.target);
        if (!input) return;
        const visible = input.type === "text";
        input.type = visible ? "password" : "text";
        button.innerHTML = visible ? '<i class="fa-regular fa-eye"></i>' : '<i class="fa-regular fa-eye-slash"></i>';
      });
    });
  }

  function initOtpInputs() {
    document.querySelectorAll(".otp-grid input").forEach((input, index, list) => {
      input.addEventListener("input", () => {
        input.value = input.value.replace(/\D/g, "").slice(0, 1);
        if (input.value && list[index + 1]) list[index + 1].focus();
      });
      input.addEventListener("keydown", (event) => {
        if (event.key === "Backspace" && !input.value && list[index - 1]) list[index - 1].focus();
      });
    });
  }

  function initCourseFilters() {
    const search = document.getElementById("courseSearch");
    const filterButtons = document.querySelectorAll("[data-filter]");
    const items = document.querySelectorAll(".course-item");
    const empty = document.getElementById("courseEmpty");
    let activeFilter = "all";

    function applyFilters() {
      const query = search ? search.value.trim().toLowerCase() : "";
      let visibleCount = 0;

      items.forEach((item) => {
        const matchesCategory = activeFilter === "all" || item.dataset.category === activeFilter;
        const matchesSearch = !query || item.dataset.title.includes(query);
        const visible = matchesCategory && matchesSearch;
        item.classList.toggle("d-none", !visible);
        if (visible) visibleCount += 1;
      });

      if (empty) empty.classList.toggle("d-none", visibleCount !== 0);
    }

    if (search) search.addEventListener("input", applyFilters);
    filterButtons.forEach((button) => {
      button.addEventListener("click", () => {
        activeFilter = button.dataset.filter;
        filterButtons.forEach((item) => item.classList.remove("active"));
        button.classList.add("active");
        applyFilters();
      });
    });
  }

  window.addEventListener("load", () => {
    if (loader) loader.classList.add("is-hidden");
  });

  window.addEventListener("scroll", handleScroll, { passive: true });
  handleScroll();

  if (backToTop) {
    backToTop.addEventListener("click", () => window.scrollTo({ top: 0, behavior: "smooth" }));
  }

  if (themeToggle) {
    const savedTheme = localStorage.getItem("learnsphere-theme") || "light";
    setTheme(savedTheme);
    themeToggle.addEventListener("click", () => {
      setTheme(root.getAttribute("data-theme") === "dark" ? "light" : "dark");
    });
  }

  animateCounters();
  initRippleButtons();
  initPasswordToggles();
  initOtpInputs();
  initCourseFilters();
})();
