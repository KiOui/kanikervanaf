let selectionItemList = document.getElementById('subscriptions-list');
let selectionItemTotal = document.getElementById('subscriptions-list-total');

function create_basket_item(name, id, price, can_email, can_letter) {

    let menulink = `<div class="menu-link"><input type="checkbox" class="normal-checkbox" onchange="toggle_checkbox(this,${id},${price},\x27${name}\x27,${can_email},${can_letter});" checked id="checkbox-basket-${id}"></input><label for="checkbox-basket-${id}">__name__</label><div class="icons">__icon_email__ __icon_letter__</div></div>`;

    if (can_email) {
        menulink = menulink.replace("__icon_email__", "<i class='fas fa-at'></i>");
    }
    else {
        menulink = menulink.replace("__icon_email__", "");
    }

    if (can_letter) {
        menulink = menulink.replace("__icon_letter__", "<i class='far fa-envelope'></i>");
    }
    else {
        menulink = menulink.replace("__icon_letter__", "");
    }

    return menulink.replace("__name__", name);
}

function create_basket(list) {
	if (list.length === 0) {
		selectionItemList.innerHTML = "Er staan nog geen abonnementen in deze lijst, kies wat abonnementen uit om op te zeggen!";
		selectionItemTotal.innerHTML = "€0,00";
	}
	else {
		let total = 0;
		let html = "U heeft de volgende abonnementen geselecteerd om op te zeggen:";
		for (let i = 0; i < list.length; i++) {
			html += create_basket_item(list[i].name, list[i].id, list[i].price, list[i].has_email, list[i].has_letter);
			if (list[i].price != null && !isNaN(list[i].price)) {
				total = total + parseFloat(list[i].price);
			}
		}
		selectionItemList.innerHTML = html;
		update_total_price(total);
	}
}

function renew_list() {
	let list = get_list();
	create_basket(list);
}

function update_total_price(price) {
	if (price == null) {
		price = 0;
	}
	if (price > 0) {
		price = price.toFixed(2);
		price = price.toString().replace('.', ',');
		selectionItemTotal.innerHTML = "€ " + price;
	}
	else {
		selectionItemTotal.innerHTML = "€0,00";
	}
}

