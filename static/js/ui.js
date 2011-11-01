function init_ui() {
	refreshServerList();
	selectMainPage('server-page');

}

function refreshServerList() {
	var servers = currentMeta.ice_call('getAllServers', function(result) {
		var serverList = $('#server-list tbody').empty();
		$(result).each(function() {
			console.log('handling result', this);
			serverList.append(
				$('<tr>').append(
					$('<td>').text('loading'),
					$('<td>').text('loading'),
					$('<td>').text('loading'),
					$('<td>').text('loading'),
					$('<td>').text('loading')
				)
			)
		});

	// enable sorting
	$('#server-list').tablesorter({ sortList: [[0,0]] });
	});
}

function selectMainPage(id) {
	var footer = $('footer');
	footer.remove();
	$('.mainpage').hide();
	$('#' + id).append(footer).show();
}
