function transformToICEObject(o) {
	$(o).each(function() {
		if (o['$ICEREF']) {
			// make object an ICEObject
			o.__proto__ = ICEObject.prototype;
		}
	});
}

function ICEObject(iceString) {
	this['$ICEREF'] = iceString;
}


ICEObject.prototype.ice_call = function (funcname, onReturn) {
	// collect args
	var args = Array.prototype.slice.call(arguments, 2);

	console.log('calling ', funcname, ' on ', this, ' with args ', args);

	// make request
	$.ajax({
				data: JSON.stringify(
				   {args: args,
					target: this['$ICEREF'],
					method_name: funcname}),
				success: function(data, textStatus, jqXHR) {
						if (! data.error) {
							var returnValue = data.returnValue;
							transformToICEObject(returnValue);
							console.log('result of ' + funcname + ' call:', returnValue);
							if (onReturn) onReturn(returnValue);
						} else {
							console.log('error occured', data);
						}
					},
				url: $API_CALL,
				type: 'POST',
				contentType: 'application/json; charset=utf-8'
			});
}
