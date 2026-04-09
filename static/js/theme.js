/**
 * Unified Theme Management for TicketAI
 * Handles theme persistence, early application to avoid FOUC,
 * and synchronized UI updates across all pages.
 */

(function() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    const root = document.documentElement;
    
    // Apply theme immediately (this script should be in <head>)
    if (savedTheme === 'dark') {
        root.classList.add('dark');
    } else {
        root.classList.remove('dark');
    }

    // Function to update icon labels if they exist
    function updateThemeIcons(isDark) {
        const icon = isDark ? '☀️' : '🌙';
        const desktopIcon = document.getElementById('themeIcon');
        const mobileIcon = document.getElementById('themeIconMobile');
        
        if (desktopIcon) desktopIcon.textContent = icon;
        if (mobileIcon) mobileIcon.textContent = icon;
    }

    // Main toggle function
    window.toggleTheme = function() {
        const isDark = root.classList.toggle('dark');
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
        updateThemeIcons(isDark);
    };

    // Initialize listeners when DOM is ready
    document.addEventListener('DOMContentLoaded', () => {
        const themeToggle = document.getElementById('themeToggle');
        const themeToggleMobile = document.getElementById('themeToggleMobile');
        
        if (themeToggle) {
            themeToggle.addEventListener('click', window.toggleTheme);
        }
        
        if (themeToggleMobile) {
            themeToggleMobile.addEventListener('click', window.toggleTheme);
        }

        // Final sync of icons in case they were rendered as placeholders
        updateThemeIcons(root.classList.contains('dark'));
    });
})();
