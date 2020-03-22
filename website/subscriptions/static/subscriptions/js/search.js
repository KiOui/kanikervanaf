var inputBox = document.getElementById('searchfor');
var categoryBox = document.getElementById('addition-categories');
var selectionBox = document.getElementById('selection-container-id');

let typingTimer;
let typingInterval = 200;

var feedback_form = '/feedback';

var current_search_index = 0;

function get_search() {
	var list = get_list();
	var inputted = inputBox.value;
	if (inputted == "") {

	}
	else {
		query(inputted, list);
	}
}

function redirect_subscription() {
	jQuery(document).ready(function($) {
		var inputted = inputBox.value;
		window.open(feedback_form + '?subscription=' + inputted);
	});
}

function query(search, list) {
	jQuery(function($) {
		current_search_index = current_search_index + 1;
		var data = {
			'action': 'deregister_categories',
			'option': 'search',
			'maximum': 5,
			'name': search,
			'index': current_search_index
		}
		$.ajax({type: 'POST', url:ajax_vars.ajax_url, data, dataType:'json', asynch: true, success:
		function(returnedData) {
			if (returnedData.error) {
				console.log(returnedData.errormsg);
			}
			else {
				if (returnedData.index == current_search_index) {
					selectionBox.innerHTML = '';
					data = returnedData.items;
					if (data.length == 0) {
						$('#selection-container-id').append("<div class='menu-link'><p>Dat abonnement is nog niet bij ons bekend! Door op de pijl te drukken kunt u doorgeven dat dit abonnement nog niet in onze database staat. Wij zullen dan ons best doen om onze database aan te vullen.<p><div class='icons' style='cursor: pointer;' onclick='redirect_subscription();'><i class='fas fa-arrow-right'></i></div></div>");
					}
					else {
						for (var i = 0; i < data.length; i++) {
							var item = create_item(data[i][0], data[i][1], data[i][2], data[i][3], data[i][4]);
							$('#selection-container-id').append(item);
						}
					}
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
	    if (inputted == "") {
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