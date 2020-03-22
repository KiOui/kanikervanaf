function send_confirmation(element, callback /*, args */) {
	var args = Array.prototype.slice.call(arguments, 2);
	var ids = get_item_ids(get_list());
	var details = get_details();
	jQuery(function($) {
	var id = element.id;
    element.style.display = "none";
	var data = {
		'action': 'deregister_categories',
		'option': "send",
		'list': ids,
		'details': details
	}
	$.ajax({type: 'POST', url:ajax_vars.ajax_url, data, dataType:'json', asynch: true, success:
		function(returnedData) {
			if (returnedData.error) {
				alert("De server heeft het verzoek tot verzenden niet geaccepteerd, heeft u een correct email-adres ingevuld onder uw gegevens?");
				element.style.display = "inline-block";
			}
			else {
				callback.apply(this, args);
			}

		}}).fail(function() {
			console.log("Error while sending email message");
			element.style.display = "inline-block";
		});
	});
}

function remove_cookies(callback /*, args */) {
	var args = Array.prototype.slice.call(arguments, 1);
	if (typeof eraseAll === "function") {
		eraseAll();
	}
	callback.apply(this, args);
}

function get_item_ids(list) {
	var ids = [];
	for (var i = 0; i < list.length; i++) {
		ids.push(list[i].id);
	}
	return ids;
}

function redirect(url) {
	window.location = '/' + url;
}