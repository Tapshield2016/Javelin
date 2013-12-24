'use strict';

/* Filters */

angular.module('shieldCommand.filters', [])

.filter('interpolate', ['version', function(version) {
    return function(text) {
      return String(text).replace(/\%VERSION\%/mg, version);
    }
  }])

.filter('byStatus', function() {
	return function(alerts, status) {
		var filtered = [];
		var statuses = [status, 'D'];
		for (var i = 0; i < alerts.length; i++) {
			if (statuses.indexOf(alerts[i].status !== -1)) {
				filtered.push(alerts[i]);
			}
		};
	}
});
