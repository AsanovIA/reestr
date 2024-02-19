/*global gettext*/
'use strict';
{
    window.addEventListener('load', function() {
        // Add anchor tag for Show/Hide link
        const fieldsets = document.querySelectorAll('fieldset.collapse');
        for (const [i, elem] of fieldsets.entries()) {
            // Don't hide if fields in this fieldset have errors
            if (elem.querySelectorAll('div.errors, ul.errorlist').length === 0) {
                // elem.classList.add('collapsed');
                const h2 = elem.querySelector('h2');
                const link = document.createElement('a');
                link.id = 'fieldsetcollapser' + i;
                link.className = 'collapse-toggle';
                link.href = '#';
                link.textContent = 'Скрыть';
                const link_show = document.createElement('a');
                link_show.id = 'fieldsetcollapsershow' + i;
                link_show.className = 'collapse-toggle-show';
                link_show.href = '#';
                link_show.textContent = 'Показать все';
                const link_hide = document.createElement('a');
                link_hide.id = 'fieldsetcollapserhide' + i;
                link_hide.className = 'collapse-toggle-hide';
                link_hide.href = '#';
                link_hide.textContent = 'Скрыть все';
                h2.appendChild(document.createTextNode(' ('));
                h2.appendChild(link);
                h2.appendChild(document.createTextNode(')  |  ('));
                h2.appendChild(link_show);
                h2.appendChild(document.createTextNode(')  |  ('));
                h2.appendChild(link_hide);
                h2.appendChild(document.createTextNode(')'));
            }
        }
        // Add toggle to hide/show anchor tag
        const toggleFunc = function(ev) {
            let links = document.querySelectorAll('.collapse-toggle');
            let fieldsets = document.querySelectorAll('fieldset.collapse');            
            if (ev.target.matches('.collapse-toggle')) {
                ev.preventDefault();
                ev.stopPropagation();
                const fieldset = ev.target.closest('fieldset');
                if (fieldset.classList.contains('collapsed')) {
                    // Show
                    ev.target.textContent = 'Скрыть';
                    fieldset.classList.remove('collapsed');
                } else {
                    // Hide
                    ev.target.textContent = 'Показать';
                    fieldset.classList.add('collapsed');
                }
            } else if (ev.target.matches('.collapse-toggle-show')) {
                // Show
                ev.preventDefault();
                ev.stopPropagation();
                for (let link of links) link.textContent = 'Скрыть';                
                for (let field of fieldsets) field.classList.remove('collapsed');
            } else if (ev.target.matches('.collapse-toggle-hide')) {
                // Hide
                ev.preventDefault();
                ev.stopPropagation();
                for (let link of links) link.textContent = 'Показать';                
                for (let field of fieldsets) field.classList.add('collapsed');
            }
        };
        document.querySelectorAll('fieldset.module').forEach(function(el) {
            el.addEventListener('click', toggleFunc);
        });
    });
}
