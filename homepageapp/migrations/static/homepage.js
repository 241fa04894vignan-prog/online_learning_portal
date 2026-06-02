// Welcome alert when page loads
window.onload = function () {

    console.log("CRT Class Portal Loaded");

};


// Get Started Button Action
document.getElementById("startBtn").addEventListener("click", function () {

    alert("Welcome to CRT Class Portal!");

    // Redirect to courses page
    window.location.href = "/courses/";

});


// Navbar Active Effect
const navLinks = document.querySelectorAll("nav ul li a");

navLinks.forEach(link => {

    link.addEventListener("mouseover", function () {

        this.style.color = "#38bdf8";

    });

    link.addEventListener("mouseout", function () {

        this.style.color = "white";

    });

});


// Card Hover Animation
const cards = document.querySelectorAll(".card");

cards.forEach(card => {

    card.addEventListener("mouseenter", function () {

        this.style.transform = "scale(1.05)";
        this.style.transition = "0.3s";

    });

    card.addEventListener("mouseleave", function () {

        this.style.transform = "scale(1)";

    });

});