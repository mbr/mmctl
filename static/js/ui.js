(function($) {
	$.fn.BootstrapPager = function(pager, callback) {
		this.each(function() {
			var pg = $('<ul>');
			if (null != pager.prev) {
				var prevLink = $('<a href="#">&larr; Previous</a>');
				var prev = $('<li class="prev">').append(prevLink);
				if (-1 != pager.prev)
					prevLink.click(function() { callback(pager.page-1); return false; });
				else {
					prev.addClass('disabled').click(function() {return false;});
				}
				pg.append(prev);
			}

			if (pager.pages)
				$.each(pager.pages, function(index, pNum) {
					var pNumInt = parseInt(pNum);
					var item = ($('<li>').append(
						$('<a href="#">')
					    .text(pNum)
					    ));
					if (isNaN(pNumInt))
						item.addClass('disabled')
						    .click(function() {return false;});
					else
						item.click(function() { callback(parseInt($(this).text())); return false; })
					if (pNumInt == pager.page)
						item.addClass('active');
					pg.append(item);
				});

			if (null != pager.next) {
				var nextLink = $('<a href="#">Next &rarr;</a>');
				var next = $('<li class="next">').append(nextLink);
				if (-1 != pager.next)
					nextLink.click(function() { callback(pager.page+1); return false; });
				else {
					next.addClass('disabled').click(function() {return false;});
				}
				pg.append(next);
			}
			$(this).empty().addClass('pagination').append(pg);
		});
	};
})( jQuery );

function init_ui() {
	/* server list page */
	$('#server-list').tablesorter();

	$('.create-server-button').click(function() {
		mmctlServer.callAPI(
			'create-server',
			null,
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

	/* global */
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

	$('ul.nav li a').click(function () {
		var target = $(this).attr('href').substring(1);

		selectMainPage(target);
		return false;
	});

	$('.alert-message').alert();


	/* load configuration */
	refreshServerList();
	refreshGlobalConfiguration();

	/* load last selected page */
	if ($.cookie('active-server'))
		loadServer($.cookie('active-server'));

	if ($.cookie('last-page'))
		selectMainPage($.cookie('last-page'));
	else
		selectMainPage('server-page');

}

function loadServerConfig(serverId) {
	mmctlServer.callAPI(
		'get-server-config' + '/' + serverId,
		null,
		function(data) {
			var serverName = data.config.registername || $('<span class="unnamed">Unnamed server</span>');
			$('#server-detail-title').empty().append('(#' + data.serverId + ') ').append(serverName);

			if (data.isRunning)
				$('#server-detail-status').text('has been running for ' + data.fuzzyUptime + '.');
			else
				$('#server-detail-status').text('is not running.');
		}
	)
}

function loadServerLog(serverId, page) {
	page = page || 1;
	mmctlServer.callAPI(
		'get-server-log' + '/' + serverId + '/' + page,
		null,
		function(data) {
			var tbl = $('#server-log tbody').empty();

			$.each(data.logEntries, function(index, entry) {
				$('<tr>').append(
					$('<td>').text(entry[3]).
						attr('title', entry[2]).
						twipsy(),
					$('<td>').text(entry[1])
				).appendTo(tbl);
			});

			$('#server-log-pagination').BootstrapPager(data.pager, function(page) {
				loadServerLog(serverId, page);
			});
		}
	)
}

function loadServer(serverId) {
	$.cookie('active-server', serverId);
	loadServerConfig(serverId);
	loadServerLog(serverId);
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

function refreshGlobalConfiguration() {
	var globalConf = mmctlServer.callAPI(
		'get-global-config',
		null,
		function(data) {
			var confList = $('#global-configuration tbody').empty();

			$.each(data.globalConf, function(k, v) {
				var help = murmurConfigurationOptions[k] || '';
				$('<tr>').append(
					$('<th>').text(k),
					$('<td>').text(v),
					$('<td>').append('<p>' + help + '</p>')
				).appendTo(confList);
			});

			var tbl = $('#global-configuration');

			if (tbl[0].config)
				tbl.trigger('update');
			else
				tbl.tablesorter({ sortList: [[0,0]] });
		}
	)
}

function refreshServerList(success) {
	var servers = mmctlServer.callAPI(
		'list-servers',
		null,
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
						$('<td class="running">').append(running),
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
					 .click(function() {
					 	 loadServer(server_id);
					 	 selectMainPage('server-detail-page');
					 })
				)
			});

			// enable sorting
			$('#server-list').trigger('update');

			if (success) success();
		});
}

function selectMainPage(id) {
	var next = $('ul.nav li a[href="#' + id + '"]').parent();

	// get current and find out if we're traveling left or right
//	var current = $('ul.nav li.active a').parent();

//	travelingRight = (-1 == next.prevAll().index(current));

	// remove all active
	$('ul.nav li').removeClass('active');
	$('.mainpage').hide();

	// set new active in menu bar
	next.addClass('active');

	// move footer and show content
	var footer = $('footer');
	footer.remove();

	$('#' + id).append(footer).show();

	// set a cookie to remember which page was visited last
	$.cookie('last-page', id, { expires: 365 })
}
