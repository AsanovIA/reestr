'use strict';
{
    window.addEventListener('load', function() {

        // Отправляем запрос
        function ajaxSend(url, params) {
            fetch(`${url}?${params}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/x-www-urlencoded',
                },
            })
                .then(response => response.json())
                .then(json => render(json))
                .catch(error => console.error(error))
        };

        //Вывод ответа от сервера
        function render(data) {
            switch (data.element) {
                case 'client_name':
                    render_client_name(data.data);
                    break;
                case 'post_abbr':
                    render_post_abbr(data.data);
                    break;
                case 'division':
                    render_select_chaild(data.data);
                    break;
            }
        };

        //Изменение инфоррмации о выбранной организации
        const clientChange = document.querySelector('select[name=client]');
        if (clientChange) {
            clientChange.addEventListener('change', () => {
                //Формирование запроса
                let url = '/valuechange/';
                let params = new URLSearchParams({
                    'element': 'client_name',
                    'id': clientChange.value
                });
                ajaxSend(url, params);
            });
        };
        function render_client_name(data) {
            //Вывод информации выбранной организации
            const clientCity = document.querySelector('#id_city');
            const clientCity_div = document.querySelector('.id_city');
            const clientINN = document.querySelector('#id_inn');
            const clientINN_div = document.querySelector('.id_inn');
            const clientDepartment = document.querySelector('#id_department');
            const clientDepartment_div = document.querySelector('.id_department');
            clientCity.value = clientCity_div.innerHTML = data.city;
            clientINN.value = clientINN_div.innerHTML = data.inn;
            clientDepartment.value = clientDepartment_div.innerHTML = data.department__name;
        };

        const postChange = document.querySelector('select[name=post]');
        if (postChange) {
            postChange.addEventListener('change', () => {
                //Формирование запроса
                let url = '/valuechange/';
                let params = new URLSearchParams({
                    'element': 'post_abbr',
                    'id': postChange.value
                });
                ajaxSend(url, params);
            });
        };
        function render_post_abbr(data) {
            //Вывод информации выбранной организации
            const post_abbr = document.querySelector('#id_post_abbr');
            const post_abbr_div = document.querySelector('.id_post_abbr');
            post_abbr.value = post_abbr_div.innerHTML = data.abbr;
        };

        //Изменение содержимого субподразделения при выборе подразделения
        const select_parent = document.querySelector('select[name=division]');
        const select_chaild = document.querySelector('select[name=sub_division]');
        if (select_parent) {
            select_parent.addEventListener('change', () => {
                //Формирование запроса                
                let url = '/valuechange/';
                let params = new URLSearchParams({
                    'element': 'division',
                    'id': select_parent.value
                });
                ajaxSend(url, params);
            });
        };

        //Изменение значений в дочернем select
        function render_select_chaild(data) {            
            select_chaild.innerHTML = '';// Очистка select
            const option = document.createElement('option');
            option.value = '';
            option.text = '---------';
            select_chaild.appendChild(option);
            for (let index in data) {
                const option = document.createElement('option');
                option.value = data[index]['id'];
                option.text = data[index]['text'];
                select_chaild.appendChild(option);
            }
        };
    })
}
