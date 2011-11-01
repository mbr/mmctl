function mmctlAPI(baseUrl, error) {
	this.baseUrl = baseUrl;
	this.error = error;
}

mmctlAPI.prototype.callAPI = function (funcname, args, success, opts) {
	if (! args) args = {};
	if (! opts) opts = {};

	opts.url = this.baseUrl + '/' + funcname + '/';
	opts.success = success;
	opts.contentType = 'application/json; charset=utf-8';
	opts.dataType = 'json';
	opts.error = this.error;
	opts.data = JSON.stringify(args);
	
	console.log('calling API with',opts);

	// make request
	$.ajax(opts);
}
