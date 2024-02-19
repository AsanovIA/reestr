'use strict';
{
    window.addEventListener('load', function() {

        const input_eye = document.querySelector('#input_password_eye');

        function toggle_func() {
            const password_input = document.querySelector('#id_password');
//             const icon_toggle = document.querySelector('#toggle-password');
            if (password_input.getAttribute("type") === "password") {
                password_input.setAttribute("type", "text");
//                 icon_toggle.classList.replace("fa-eye-slash", "fa-eye");
            } else {
                password_input.setAttribute("type", "password");
//                 icon_toggle.classList.replace("fa-eye", "fa-eye-slash");
            }
        }

        input_eye.addEventListener('click', toggle_func);
    })
}
