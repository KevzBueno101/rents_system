document.addEventListener('DOMContentLoaded', function () {

    // ── TOPBAR DATE ──────────────────────────────────
    const d = new Date();
    document.getElementById('currentDate').textContent = d.toLocaleDateString('en-US', {
        weekday: 'short', year: 'numeric', month: 'short', day: 'numeric'
    });

    // ── MOBILE SIDEBAR TOGGLE ─────────────────────────
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    const toggleBtn = document.querySelector('[onclick="toggleSidebar()"]');

    window.toggleSidebar = function () {
        sidebar.classList.toggle('show');
        overlay.classList.toggle('show');
    };

    // ── CLOSE SIDEBAR ON OVERLAY CLICK ───────────────
    overlay.addEventListener('click', function () {
        sidebar.classList.remove('show');
        overlay.classList.remove('show');
    });

});