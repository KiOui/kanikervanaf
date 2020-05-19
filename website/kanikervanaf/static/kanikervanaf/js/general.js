var SUBSCRIPTION_LIST_COOKIE = "subscription_items";
var SUBSCRIPTION_DETAILS_COOKIE = "subscription_details";

function set_style_list(list, style, value) {
    for (let i = 0; i < list.length; i++) {
        $(list[i]).css(style, value);
    }
}

function set_text_list(list, text) {
    for (let i = 0; i < list.length; i++) {
        list[i].innerHTML = text;
    }
}

function in_list(list, id) {
	for (let i = 0; i < list.length; i++) {
		if (list[i].id === id) {
			return true;
		}
	}
	return false;
}

function toggle_checkbox(checkbox, id, price, name, has_email, has_letter, has_price) {
    let list = get_list();
    if (checkbox.checked) {
        if (!in_list(list, id)) {
            list.push({"id": id, "price": price, "name": name, "has_email": has_email, "has_letter": has_letter, "has_price": has_price});
        }
    }
    else {
        let newlist = [];
        for (let i = 0; i < list.length; i++) {
            if (list[i].id !== id) {
                newlist.push(list[i]);
            }
        }
        list = newlist;
    }
    set_list(list);
	refresh_all();
}

function get_details() {
	let cookie = getCookie(SUBSCRIPTION_DETAILS_COOKIE);
	try {
		let details = JSON.parse(cookie);
		if (details == null) {
			return {};
		}
		else {
			return details;
		}
	}
	catch (error) {
		return {};
	}
}

function set_details(details) {
	try {
		let string = JSON.stringify(details);
		setCookie(SUBSCRIPTION_DETAILS_COOKIE, string, 1);
	}
	catch(error) {
		setCookie(SUBSCRIPTION_DETAILS_COOKIE, "", 1);
	}
}

function get_list() {
	let cookie = getCookie(SUBSCRIPTION_LIST_COOKIE);
	try {
		let list = JSON.parse(cookie);
		if (list == null) {
		    return [];
        }
        else {
            return list;
        }
	}
	catch(error) {
		return [];
	}
}

function set_list(list) {
	try {
		let string = JSON.stringify(list);
		setCookie(SUBSCRIPTION_LIST_COOKIE, string, 1);
	}
	catch(error) {
        setCookie(SUBSCRIPTION_LIST_COOKIE, "", 1);
    }
}

function refresh_all() {
	if (typeof renew_search === "function") {
		renew_search();
	}
	if (typeof renew_list === "function") {
		renew_list();
	}
	if (typeof renew_categories === "function") {
		renew_categories();
	}
	if (typeof disable_buttons === "function") {
		disable_buttons();
	}
}

function setCookie(name,value,days) {
    let expires = "";
    value = encodeURI(value);
    if (days) {
        let date = new Date();
        date.setTime(date.getTime() + (days*24*60*60*1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + (value || "")  + expires + "; path=/";
}

function getCookie(name) {
    let nameEQ = name + "=";
    let ca = document.cookie.split(';');
    for(let i=0;i < ca.length;i++) {
        let c = ca[i];
        while (c.charAt(0)===' ') c = c.substring(1,c.length);
        if (c.indexOf(nameEQ) === 0) return decodeURI(c.substring(nameEQ.length,c.length));
    }
    return "";
}

function eraseAll() {
	set_details({});
	set_list([]);
}

function eraseCookie(name) {   
    document.cookie = name+'=; path=/; domain=kanikervanaf.nl; Max-Age=-99999999;';  
}

jQuery(document).ready(function($) {
	refresh_all();
});
