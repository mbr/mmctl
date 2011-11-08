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
