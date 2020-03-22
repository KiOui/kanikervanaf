let disableNoItems = document.getElementById('subscription-disable-button-no-items');
let disableNoDetails = document.getElementById('subscription-disable-button-no-details');
let disableNoAll = document.getElementById('subscription-disable-button-no-all');

function disable_buttons() {
	let itemlist = get_list();
	let details = get_details();
	if (disableNoItems) {
		if (itemlist.length > 0) {
			disableNoItems.style.display = "inline-block";
		}
		else {
			disableNoItems.style.display = "none";
		}
	}
	if (disableNoDetails) {
		if (details.email !== undefined && details.first_name !== undefined && details.email !== "" && details.first_name !== "") {
			disableNoDetails.style.display = "inline-block";
		}
		else {
			disableNoDetails.style.display = "none";
		}
	}
	if (disableNoAll) {
		if (itemlist.length > 0 && details.email !== undefined && details.first_name !== undefined && details.email !== "" && details.first_name !== "") {
			disableNoAll.style.display = "inline-block";
		}
		else {
			disableNoAll.style.display = "none";
		}
	}
}