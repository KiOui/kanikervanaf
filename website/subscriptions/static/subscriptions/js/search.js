let inputBox = document.getElementById('searchfor');
let selectionBox = document.getElementById('selection-container-id');

let typingTimer;
let typingInterval = 200;

let feedback_form = '/feedback';

let current_search_index = 0;

var PRE_CHECKBOX_SEARCH = "checkbox-search-";
var NAME_CHECKBOXES_SEARCH = "checkbox-search-list";

function toggle_search_checkboxes(checkboxes, list) {
    for (let i = 0; i < checkboxes.length; i++) {
        let checkbox = checkboxes[i];
        let id = Number(checkbox.id.replace(PRE_CHECKBOX_SEARCH, ''));
        checkbox.checked = in_list(list, id);
    }
}

function renew_search() {
	let list = get_list();
	let checkboxes = document.querySelectorAll(`input[name=${NAME_CHECKBOXES_SEARCH}`);
	toggle_search_checkboxes(checkboxes, list);
}

function create_search_item(name, id, price, can_email, can_letter, in_list) {

    let menulink = `<div class="menu-link"><input name="checkbox-search-list" type="checkbox" class="normal-checkbox" onchange="toggle_checkbox(this,${id},${price},\x27${name}\x27,${can_email},${can_letter});" __checked__ id="checkbox-search-${id}"></input><label for="checkbox-search-${id}">__name__</label><div class="icons">__icon_email__ __icon_letter__</div></div>`;

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

    if (in_list) {
    	menulink = menulink.replace("__checked__", "checked");
	}
	else {
    	menulink = menulink.replace("__checked__", "");
	}

    return menulink.replace("__name__", name);
}

function get_search() {
	let list = get_list();
	let inputted = inputBox.value;
	if (inputted === "") {
		selectionBox.innerHTML = '';
	}
	else {
		query(inputted, list);
	}
}

function redirect_subscription() {
	jQuery(document).ready(function($) {
		let inputted = inputBox.value;
		window.open(feedback_form + '?subscription=' + inputted);
	});
}

function query(search, list) {
    let csrf_token = getCookie('csrftoken');
	jQuery(function($) {
		current_search_index = current_search_index + 1;
		let data = {
			'maximum': 5,
			'query': search,
			'id': current_search_index,
            'csrfmiddlewaretoken': csrf_token
		};
		$.ajax({type: 'POST',url:SEARCH_URL, data, dataType:'json', asynch: true, success:
		function(returnedData) {
            if (returnedData.id == current_search_index) {
                selectionBox.innerHTML = '';
                data = returnedData.items;
                if (data.length === 0) {
                    selectionBox.innerHTML = "<div class='menu-link'><p>Dat abonnement is nog niet bij ons bekend! Door op de pijl te drukken kunt u doorgeven dat dit abonnement nog niet in onze database staat. Wij zullen dan ons best doen om onze database aan te vullen.<p><div class='icons' style='cursor: pointer;' onclick='redirect_subscription();'><i class='fas fa-arrow-right'></i></div></div>";
                }
                else {
                    let html = "";
                    for (let i = 0; i < data.length; i++) {
                        html += create_search_item(data[i].name, data[i].id, data[i].price, data[i].can_email, data[i].can_letter, in_list(list, data[i].id));
                    }
                    selectionBox.innerHTML = html;
                }
            }
		}}).fail(function() {
			console.log("Error while getting search results for query " + search);
		});
	});
}

jQuery(document).ready(function($) {

	inputBox.addEventListener('keyup', () => {
	    clearTimeout(typingTimer);
	    let inputted = inputBox.value;
	    if (inputted === "") {
    		selectionBox.style.display = "none";
	    }
	    else {
	    	selectionBox.style.display = "";
	    }

	    if (inputBox.value) {
	        typingTimer = setTimeout(get_search, typingInterval);
	    }
	});

});