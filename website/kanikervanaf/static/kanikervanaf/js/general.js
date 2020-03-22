var SUBSCRIPTION_LIST_COOKIE = "subscription_items";
var SUBSCRIPTION_DETAILS_COOKIE = "subscription_details";

function in_list(list, id) {
	for (let i = 0; i < list.length; i++) {
		if (list[i].id === id) {
			return true;
		}
	}
	return false;
}

function toggle_checkbox(checkbox, id, price, name, has_email, has_letter) {
    let list = get_list();
    if (checkbox.checked) {
        if (!in_list(list, id)) {
            list.push({"id": id, "price": price, "name": name, "has_email": has_email, "has_letter": has_letter});
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
		var details = JSON.parse(cookie);
	}
	catch (error) {
		return {};
	}
	if (details == null) {
		return {};
	}
	else {
		return details;
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
	if (typeof get_search === "function") {
		get_search();
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

function get_price(id, callback /*, args */) {
	let args = Array.prototype.slice.call(arguments, 2);
	jQuery(function($) {
	let data = {
		'action': 'deregister_categories',
		'option': "price",
		'id': id
	};
	$.ajax({type: 'POST', url:ajax_vars.ajax_url, data, dataType:'json', asynch: true, success:
		function(returnedData) {
			if (returnedData.error) {
				console.log(returnedData.errormsg);
			}
			else {
				args.unshift(returnedData.price);
				callback.apply(this, args);
			}

		}}).fail(function() {
			console.log("Error while getting the price of " + id);
		});
	});
}

function get_post_details(id, callback) {
	let args = Array.prototype.slice.call(arguments, 1);
	jQuery(function($) {
		let data = {
			'action': 'deregister_categories',
			'option': "details",
			'id': id
		};
		$.ajax({type: 'POST', url:ajax_vars.ajax_url, data, dataType:'json', asynch: true, success:
				function(returnedData) {
					if (returnedData.error) {
						console.log(returnedData.errormsg);
					}
					else {
						args.unshift(returnedData.details);
						callback.apply(this, args);
					}

				}}).fail(function() {
			console.log("Error while getting the details of " + id);
		});
	});
}

function query_total_price(list, callback /*, args */) {
	let args = Array.prototype.slice.call(arguments, 2);
	list = JSON.stringify(list);
	jQuery(function($) {
		let data = {
			'action': 'deregister_categories',
			'option': 'total_price',
			'list': list
		};
		$.ajax({type: 'POST', url:ajax_vars.ajax_url, data, dataType:'json', asynch: true, success:
		function(returnedData) {
			if (returnedData.error) {
				console.log(returnedData.errormsg);
			}
			else {
				args.unshift(returnedData.total);
				callback.apply(this, args);
			}

		}}).fail(function() {
			console.log("Error while getting search results for query " + search);
		});
		return "";
	});
}

function query_id(id, callback /*, args */) {
	let args = Array.prototype.slice.call(arguments, 2);
	jQuery(function($) {
		let data = {
			'action': 'deregister_categories',
			'option': 'data',
			'id': id
		};
		$.ajax({type: 'POST', url:ajax_vars.ajax_url, data, dataType:'json', asynch: true, success:
		function(returnedData) {
			if (returnedData.error) {
				console.log(returnedData.errormsg);
			}
			else {
				if (returnedData.name !== "") {
					args.unshift(returnedData.data.price);
					args.unshift(id);
					args.unshift(returnedData.data.name);
					callback.apply(this, args);
				}
				else {
					console.log("Error, id " + id + " does not exist.");
				}
			}

		}}).fail(function() {
			console.log("Error while getting search results for query " + search);
		});
	});
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
