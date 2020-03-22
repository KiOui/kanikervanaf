var PRE_CHECKBOX = "checkbox-";
var NAME_CHECKBOXES = "checkbox-category-list";

function toggle_checkboxes(checkboxes, list) {
    for (let i = 0; i < checkboxes.length; i++) {
        let checkbox = checkboxes[i];
        let id = Number(checkbox.id.replace(PRE_CHECKBOX, ''));
        checkbox.checked = in_list(list, id);
    }
}

function renew_categories() {
	let list = get_list();
	let checkboxes = document.querySelectorAll(`input[name=${NAME_CHECKBOXES}`);
	toggle_checkboxes(checkboxes, list);
}