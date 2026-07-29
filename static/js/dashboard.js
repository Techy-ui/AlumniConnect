// ==========================================
// AlumniConnect Dashboard
// dashboard.js
// ==========================================

document.addEventListener("DOMContentLoaded", () => {

    const sidebar = document.getElementById("sidebar");
    const menuToggle = document.getElementById("menuToggle");

    // ===============================
    // Mobile Sidebar Toggle
    // ===============================

    if(menuToggle){

        menuToggle.addEventListener("click", () => {

            sidebar.classList.toggle("active");

        });

    }

    // ===============================
    // Close Sidebar when clicking outside
    // ===============================

    document.addEventListener("click", (e) => {

        if(window.innerWidth <= 992){

            if(
                !sidebar.contains(e.target) &&
                !menuToggle.contains(e.target)
            ){

                sidebar.classList.remove("active");

            }

        }

    });

    // ===============================
    // Active Sidebar Link
    // ===============================

    const current = window.location.pathname;

    document.querySelectorAll(".sidebar-menu a").forEach(link=>{

        if(current === link.getAttribute("href")){

            link.classList.add("active");

        }

    });

    // ===============================
    // Fade Animation
    // ===============================

    document.querySelectorAll(".card").forEach((card,index)=>{

        card.style.opacity="0";

        card.style.transform="translateY(20px)";

        setTimeout(()=>{

            card.style.transition=".4s";

            card.style.opacity="1";

            card.style.transform="translateY(0)";

        },100*index);

    });

    // ===============================
    // Bootstrap Tooltips
    // ===============================

    const tooltipTriggerList = document.querySelectorAll(
        '[data-bs-toggle="tooltip"]'
    );

    tooltipTriggerList.forEach(el=>{

        new bootstrap.Tooltip(el);

    });

});s