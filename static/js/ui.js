function init_ui() {
	$('.alert-message').alert();
	refreshServerList();

	$('#server-list').tablesorter();

	$('.create-server-button').click(function() {
		mmctlServer.callAPI(
			'create-server',
			{},
			function(data) {
				refreshServerList(function() {
					// scroll to newly created item
					var newRow = $('tr[data-server-id=' + data.server_id + ']'); 
					$.scrollTo(newRow);
					newRow.
					twipsy({
						'fallback': 'A new server has been created.',
						'placement': 'below',
						'delayIn': 1500,
						'trigger': 'manual'}).
					twipsy('show');

					// hide twipsy after one click
					$(document).one('click', function() { newRow.data('twipsy').hide(); });
				});
			},
			{'type': 'POST'});
	});

	$('#refresh-server-list-button').click(function() {
		refreshServerList();
	});

	$('.table-check-all input[type="checkbox"]').change(function() {
		$(this).closest('table').find('input[type="checkbox"][name="' + this.name + '[]"]').attr('checked', $(this).attr('checked'));
	});

	$('.table-check-all').unbind('click').removeClass('header');

	$('#confirm-dialog').modal({
		'keyboard': true,
		'backdrop': 'static'
	});
	$('#confirm-dialog-cancel').click(function() {
		$('#confirm-dialog').modal('hide');
	});

	selectMainPage('server-page');
}

function confirmDialog(title, message, action, actionClass, on_ok) {
	var dlg = $('#confirm-dialog');
	dlg.find('h3').empty().append(title);
	dlg.find('p').empty().append(message);
	dlg.find('#confirm-dialog-confirm')
		.empty()
		.removeClass('danger')
		.removeClass('success')
		.removeClass('primary')
		.addClass(actionClass)
		.append(action)
		.one('click', function() {
			if (on_ok) on_ok();
			// perform action, at most once
			dlg.modal('hide');
		});

	dlg.bind('hide', function() {
		// remove signal handlers, so its hard to accidentally trigger an old action
		dlg.find('#confirm-dialog-confirm').unbind();

		return false;
	});

	dlg.modal('show');
}

function createGlobalAlert(alertClass, message) {
	$('<div class="alert-message fade in" data-alert="alert">').
	addClass(alertClass).
	append('<a class="close" href="#">&times;</a>').
	append(message).
	appendTo($('#global-alerts'));
}

function refreshServerList(success) {
	var servers = mmctlServer.callAPI(
		'list-servers',
		{},
		function(data) {
			// clear server list
			var serverList = $('#server-list tbody').empty();

			// append rows
			$(data.servers).each(function() {
				var running = $('<span>');
				var server_id = this.id;
				var server_name = this.name;
				var server_address = this.address;

				if (this.running) {
					running.text('up ' + this.fuzzy_uptime).
					prepend($('<button class="btn small">').text("stop")
							.click(function() {
								mmctlServer.callAPI(
									'stop-server',
									{'server_id': server_id},
									function(data) {
										refreshServerList();
									},
									{'type': 'post'});
								$(this).addClass('disabled').attr('disabled', true);
							}));
				} else {
					running.
					prepend($('<button class="btn small primary">').text("start")
							.click(function() {
								mmctlServer.callAPI(
									'start-server',
									{'server_id': server_id},
									function(data) {
										refreshServerList();
									},
									{'type': 'post'});
								$(this).addClass('disabled').attr('disabled', true);
							}));
				}

				serverList.append(
					$('<tr class="clickable">').append(
						$('<td class="small">').text(server_id),
						$('<td class="large">').text(server_name),
						$('<td class="medium">').text(server_address),
						$('<td>').append(running),
						$('<td class="small">').text(this.users + '/' + this.maxusers),
						$('<td class="small">').append($('<button class="btn small danger">Del</button>')
							.click(function() {
								var delButton = this;
								confirmDialog(
									'Confirm deleting server',
									'Are you sure you want to delete server #' +
									server_id + ' "' +
									server_name + '" (' + server_address + ')?',
									'Delete',
									'danger',
									function() {
										$(delButton).addClass('disabled').attr('disabled', true);
										mmctlServer.callAPI(
											'delete-server',
											{server_id: server_id},
											function() { refreshServerList(); },
											{'type': 'post'})
									});
							}))
					).attr('data-server-id', this.id)
				)
			});

			// enable sorting
			$('#server-list').trigger('update');

			if (success) success();
		});
}

function selectMainPage(id) {
	var footer = $('footer');
	footer.remove();
	$('.mainpage').hide();
	$('#' + id).append(footer).show();
}
