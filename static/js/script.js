

// Auto move from landing to dashboard only on first load
setTimeout(() => {
  const landing = document.getElementById("landing");
  const dashboard = document.getElementById("dashboard");

  if (landing && dashboard && dashboard.classList.contains("hidden")) {
    landing.style.display = "none";
    dashboard.classList.remove("hidden");
  }
}, 3000);



function animateCounters() {
  const counters = document.querySelectorAll('[data-value]');
  
  counters.forEach(counter => {
    const target = +counter.getAttribute('data-value');
    let current = 0;
    const increment = target / 100;

    const updateCounter = () => {
      current += increment;
      if (current < target) {
        counter.innerText = Math.ceil(current);
        requestAnimationFrame(updateCounter);
      } else {
        counter.innerText = target;
      }
    };

    updateCounter();
  });
}

// Run counter when dashboard is visible
window.onload = () => {
  const dashboard = document.getElementById("dashboard");
  if (!dashboard.classList.contains("hidden")) {
    animateCounters();
  }
};
