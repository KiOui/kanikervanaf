let firstname_select = document.getElementById('firstname');
let lastname_select = document.getElementById('lastname');
let address_select = document.getElementById('address');
let postalcode_select = document.getElementById('postalcode');
let residence_select = document.getElementById('residence');
let email_select = document.getElementById('email');

function update_cookie(first_name, second_name, address, postal_code, residence, email) {
	let details = {'first_name': first_name, 'second_name': second_name, 'address': address, 'postal_code': postal_code, 'residence': residence, 'email': email};
	set_details(details);
}

function update() {
	update_cookie(firstname_select.value, lastname_select.value, address_select.value, postalcode_select.value, residence_select.value, email_select.value);
	refresh_all();
}

function putback_details() {
	let cookie = get_details();
	if (cookie.first_name) {
		firstname_select.value = cookie.first_name;
	}
	if (cookie.second_name) {
		lastname_select.value = cookie.second_name;
	}
	if (cookie.address) {
		address_select.value = cookie.address;
	}
	if (cookie.postal_code) {
		postalcode_select.value = cookie.postal_code;
	}
	if (cookie.residence) {
		residence_select.value = cookie.residence;
	}
	if (cookie.email) {
		email_select.value = cookie.email;
	}
}

function register_keyup() {
	jQuery(function($) {
		$('#firstname').keyup(function() {
			update();
		});
		$('#lastname').keyup(function() {
			update();
		});
		$('#address').keyup(function() {
			update();
		});
		$('#postalcode').keyup(function() {
			update();
		});
		$('#residence').keyup(function() {
			update();
		});
		$('#email').keyup(function() {
			update();
		});
	});
}

jQuery(document).ready(function($) {
	register_keyup();
	putback_details();
	update();
});