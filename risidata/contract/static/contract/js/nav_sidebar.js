'use strict';
{
    const toggleNavSidebar = document.getElementById('toggle-nav-sidebar');
    if (toggleNavSidebar !== null) {
        const navSidebar = document.getElementById('nav-sidebar');
        const main = document.getElementById('main');
        let navSidebarIsOpen = sessionStorage.getItem('django.contract.SidebarIsOpen');
        if (navSidebarIsOpen === null) {
            navSidebarIsOpen = 'true';
        }
        main.classList.toggle('shifted', navSidebarIsOpen === 'true');
        navSidebar.setAttribute('aria-expanded', navSidebarIsOpen);

        toggleNavSidebar.addEventListener('click', function() {
            if (navSidebarIsOpen === 'true') {
                navSidebarIsOpen = 'false';
            } else {
                navSidebarIsOpen = 'true';
            }
            sessionStorage.setItem('django.contract.SidebarIsOpen', navSidebarIsOpen);
            main.classList.toggle('shifted');
            navSidebar.setAttribute('aria-expanded', navSidebarIsOpen);
        });
    }

    function initSidebarQuickFilter() {
        const options = [];
        const navSidebar = document.getElementById('nav-sidebar');
        const nav = document.getElementById('nav-filter');
        const filter = document.getElementById('filter-filter');
        if (!navSidebar || !(nav || filter)) {
            return;
        }
        navSidebar.querySelectorAll('table.menu th[scope=row] a').forEach((container) => {
            options.push({title: container.innerHTML, node: container});
        });
        navSidebar.querySelectorAll('table.filter caption').forEach((container) => {
            options.push({title: container.innerHTML, node: container});
        });

        function checkValue(event) {
            let filterValue = event.target.value;
            if (filterValue) {
                filterValue = filterValue.toLowerCase();
            }
            if (event.key === 'Escape') {
                filterValue = '';
                event.target.value = ''; // clear input
            }
            let matches = false;
            for (const o of options) {
                let displayValue = '';
                if (filterValue) {
                    if (o.title.toLowerCase().indexOf(filterValue) === -1) {
                        displayValue = 'none';
                    } else {
                        matches = true;
                    }
                }
                // show/hide parent <TR>
                if (nav) {
                    o.node.parentNode.parentNode.style.display = displayValue;
                } else {
                    o.node.parentNode.style.display = displayValue;
                }

            }
            if (!filterValue || matches) {
                event.target.classList.remove('no-results');
            } else {
                event.target.classList.add('no-results');
            }
            sessionStorage.setItem('django.contract.SidebarFilterValue', filterValue);
        }

//        const nav = document.getElementById('nav-filter');
//        const filter = document.getElementById('filter-filter');
        if (nav) {
            nav.addEventListener('change', checkValue, false);
            nav.addEventListener('input', checkValue, false);
            nav.addEventListener('keyup', checkValue, false);
        } else {
            filter.addEventListener('change', checkValue, false);
            filter.addEventListener('input', checkValue, false);
            filter.addEventListener('keyup', checkValue, false);
        }

        const storedValue = sessionStorage.getItem('django.contract.SidebarFilterValue');
        if (storedValue) {
            nav.value = storedValue;
            checkValue({target: nav, key: ''});
        }
    }
    window.initSidebarQuickFilter = initSidebarQuickFilter;
    initSidebarQuickFilter();
}
