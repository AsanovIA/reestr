'use strict';
{
    window.addEventListener('load', function() {
        //Расчет и отображение суммы НДС и цены с НДС договора
        const priceNoNDS = document.getElementById('id_price_no_nds');
        const nds = document.getElementById('id_nds');
        const summNDS = document.querySelector('#id_summ_nds');
        const summNDS_div = document.querySelector('.id_summ_nds');    
        const pricePlusNDS = document.querySelector('#id_price_plus_nds');
        const pricePlusNDS_div = document.querySelector('.id_price_plus_nds');

        function checkValue() {
            summNDS.value = parseFloat(((priceNoNDS.value * 100 * nds.value) / 10000).toFixed(3));
            summNDS_div.innerHTML = parseFloat(((priceNoNDS.value * 100 * nds.value) / 10000).toFixed(3));
            if (summNDS.value < 0) summNDS.value = 0
            if (summNDS_div.innerHTML < 0) summNDS_div.innerHTML = 0

            pricePlusNDS.value = parseFloat(((+priceNoNDS.value * 100 + +summNDS.value * 100) / 100).toFixed(3));
            pricePlusNDS_div.innerHTML = parseFloat(((+priceNoNDS.value * 100 + +summNDS_div.innerHTML * 100) / 100).toFixed(3));
            if (pricePlusNDS.value < 0) pricePlusNDS.value = 0  
            if (pricePlusNDS_div.innerHTML < 0) pricePlusNDS_div.innerHTML = 0   
             
            if (nds.value > 100) nds.value = 100
            if (nds.value < 0) nds.value = 0
            if (priceNoNDS.value < 0) priceNoNDS.value = 0        
        }

        priceNoNDS.addEventListener('change', checkValue, false);
        priceNoNDS.addEventListener('input', checkValue, false);
        priceNoNDS.addEventListener('keyup', checkValue, false);
        nds.addEventListener('change', checkValue, false);
        nds.addEventListener('input', checkValue, false);
        nds.addEventListener('keyup', checkValue, false);
    })
}
