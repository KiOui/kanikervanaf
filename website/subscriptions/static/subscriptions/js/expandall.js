function expand_all(element, remove) {
	let overlapping_div = document.getElementById(element);
	for (let i = 0; i < overlapping_div.children.length; i++) {
		overlapping_div.children[i].style.display = '';
	}
	let remove_item = document.getElementById(remove);
	remove_item.style.display = 'none';
}