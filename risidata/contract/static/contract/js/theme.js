'use strict';
{
    window.addEventListener('load', function(e) {

        function setTheme(mode) {
            if (mode !== "light" && mode !== "dark") {
                console.error(`Got invalid theme mode: ${mode}. Resetting to auto.`);
                mode = "light";
            }
            document.documentElement.dataset.theme = mode;
            localStorage.setItem("theme", mode);
        }

        function cycleTheme() {
            const currentTheme = localStorage.getItem("theme") || "light";
            const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;

            if (prefersDark) {
                // Auto (dark) -> Light -> Dark
                if (currentTheme === "dark") setTheme("light")
                else setTheme("dark");
            } else {
                // Auto (light) -> Dark -> Light
                if (currentTheme === "light") setTheme("dark")
                else setTheme("light");
            }
        }

        function initTheme() {
            // set theme defined in localStorage if there is one, or fallback to auto mode
            const currentTheme = localStorage.getItem("theme");
            currentTheme ? setTheme(currentTheme) : setTheme("light");
        }

        function setupTheme() {
            // Attach event handlers for toggling themes
            const buttons = document.getElementsByClassName("theme-toggle");
            Array.from(buttons).forEach((btn) => {
                btn.addEventListener("click", cycleTheme);
            });
            initTheme();
        }

        setupTheme();
    });
}
