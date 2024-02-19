'use strict';
{
    window.addEventListener('load', function() {
        //Автоматическое заполнение полей login и e-mail формы
        const TRANSTABLE = [
            // lower
            ["а", "a"],
            ["б", "b"],
            ["в", "v"],
            ["г", "g"],
            ["д", "d"],
            ["е", "e"],
            ["ё", "e"],
            ["ж", "zh"],
            ["з", "z"],
            ["и", "i"],
            ["й", "i"],
            ["к", "k"],
            ["л", "l"],
            ["м", "m"],
            ["н", "n"],
            ["о", "o"],
            ["п", "p"],
            ["р", "r"],
            ["с", "s"],
            ["т", "t"],
            ["у", "u"],
            ["ф", "f"],
            ["х", "kh"],
            ["ц", "ts"],
            ["ч", "ch"],
            ["ш", "sh"],
            ["щ", "shch"],
            ["ъ", "ie"],
            ["ы", "y"],
            ["ь", ""],
            ["э", "e"],
            ["ю", "iu"],
            ["я", "ia"],
            // upper
            ["А", "A"],
            ["Б", "B"],
            ["В", "V"],
            ["Г", "G"],
            ["Д", "D"],
            ["Е", "E"],
            ["Ё", "E"],
            ["Ж", "ZH"],
            ["З", "Z"],
            ["И", "I"],
            ["Й", "I"],
            ["К", "K"],
            ["Л", "L"],
            ["М", "M"],
            ["Н", "N"],
            ["О", "O"],
            ["П", "P"],
            ["Р", "R"],
            ["С", "S"],
            ["Т", "T"],
            ["У", "U"],
            ["Ф", "F"],
            ["Х", "KH"],
            ["Ц", "TS"],
            ["Ч", "CH"],
            ["Ш", "SH"],
            ["Щ", "SHCH"],
            ["Ъ", "IE"],
            ["Ы", "Y"],
            ["Ь", ""],
            ["Э", "E"],
            ["Ю", "IU"],
            ["Я", "IA"],
            ];

        function translit(text) {
            if (typeof text === "string" && text.length > 0) {
                if (text.length === 1) {
                    const result = TRANSTABLE.find(([symbol]) => symbol === text);
                    if (result) {
                        const [symbol_in, symbol_out] = result;
                        return symbol_out;
                    };
                } else {
                    for (let [symbol_in, symbol_out] of TRANSTABLE) {
                        text = text.replace(new RegExp(symbol_in, "g"), symbol_out);
                    }
                };
            }
            return text;
        }

        const first_name = document.querySelector('#id_first_name');
        const last_name = document.querySelector('#id_last_name');
        const middle_name = document.querySelector('#id_middle_name');

        const userprofile = document.querySelector('#userprofile_form');
        let username, username_div, email, email_div;
        if (userprofile) {
            username = document.querySelector('#id_username');
            username_div = document.querySelector('.id_username');
            email = document.querySelector('#id_email');
            email_div = document.querySelector('.id_email');

        }

        function checkValue(event) {
            let last = last_name.value.length > 0 ? last_name.value[0].toUpperCase() : '';
            let first = first_name.value.length > 0 ? first_name.value[0].toUpperCase() : '';
            let middle = middle_name.value.length > 0 ? middle_name.value[0].toUpperCase() : '';
            if (last_name.value.length > 1) {
                last = last + last_name.value.substring(1).toLowerCase();
            };

            const firstdot = first ? first + '.' : '';
            const middledot = middle ? middle + '.' : '';

            first = translit(first);
            middle = translit(middle);
            last = translit(last);
            
            if (userprofile) {                
                let login = first + middle + last;
                if (login) {
                    username.value = login;
                    if (username_div) username_div.innerHTML = login;
                };
                if (first || middle || last) {
                    email.value = login + '@niipribor.ru';
                    if (email_div) email_div.innerHTML = login + '@niipribor.ru';
                };
            };
        };

        first_name.addEventListener('change', checkValue, false);
        first_name.addEventListener('input', checkValue, false);
        first_name.addEventListener('keyup', checkValue, false);
        last_name.addEventListener('change', checkValue, false);
        last_name.addEventListener('input', checkValue, false);
        last_name.addEventListener('keyup', checkValue, false);
        middle_name.addEventListener('change', checkValue, false);
        middle_name.addEventListener('input', checkValue, false);
        middle_name.addEventListener('keyup', checkValue, false);
    })
}
