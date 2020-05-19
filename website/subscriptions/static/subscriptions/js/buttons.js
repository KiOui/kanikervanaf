let disableNoItems = document.getElementsByClassName('subscription-disable-button-no-items');
let disableNoDetails = document.getElementsByClassName('subscription-disable-button-no-details');
let disableNoAll = document.getElementsByClassName('subscription-disable-button-no-all');

function disable_buttons() {
	let itemlist = get_list();
	let details = get_details();
	if (disableNoItems.length > 0) {
		if (itemlist.length > 0) {
			set_style_list(disableNoItems, "display", "inline-block");
		}
		else {
			set_style_list(disableNoItems, "display", "none");
		}
	}
	if (disableNoDetails.length > 0) {
		if (details.email !== undefined && details.first_name !== undefined && details.email !== "" && details.first_name !== "") {
			set_style_list(disableNoDetails, "display", "inline-block");
		}
		else {
			set_style_list(disableNoDetails, "display", "none");
		}
	}
	if (disableNoAll.length > 0) {
		if (itemlist.length > 0 && details.email !== undefined && details.first_name !== undefined && details.email !== "" && details.first_name !== "") {
			set_style_list(disableNoAll, "display", "inline-block");
		}
		else {
			set_style_list(disableNoAll, "display", "none");
		}
	}
}