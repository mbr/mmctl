function ServerConfiguration(localConf, defaultConf) {
	this.updateConf(localConf, defaultConf);
}

ServerConfiguration.prototype.updateConf = function(localConf, defaultConf) {
	this.localConf = localConf;
	this.defaultConf = defaultConf;
	this.changedConf = {};

	$(this).trigger('update');

	var me = this;
	$.each(this.getAllValues(), function(k, v) { me._update(k, v) });
}

ServerConfiguration.prototype.getValue = function(key) {
	if (undefined != this.changedConf[key]) return this.changedConf[key];
	if (undefined != this.localConf[key]) return this.localConf[key];
	return this.defaultConf[key];
}

ServerConfiguration.prototype.isLocal = function(key) {
	return (undefined != this.changedConf[key] ||
	       undefined != this.localConf[key]);
}

ServerConfiguration.prototype.setValue = function(key, value) {
	this.changedConf[key] = value;
	$(this).trigger('changed', key, value);

	this._update(key, value);
}

ServerConfiguration.prototype._update = function(key, value) {
	/* update all linked */
	$('*[data-config-link="' + key + '"]').val(function() {
		return value;
	}).trigger('config-update');
	$('input[type="checkbox"][data-config-link="' + key + '"]').attr(
		'checked',
		('false' != value && '0' != value && '' != value)
	);
	$('span[data-config-link="' + key + '"]').text(value);
}

ServerConfiguration.prototype.getAllValues = function() {
	return $.extend({}, this.defaultConf, this.localConf, this.changedConf);
}

ServerConfiguration.prototype.getChangedValues = function() {
	return $.extend({}, this.changedConf);
}

ServerConfiguration.prototype.hasChanged = function(key) {
	return Boolean(this.changedConf[key]);
}
