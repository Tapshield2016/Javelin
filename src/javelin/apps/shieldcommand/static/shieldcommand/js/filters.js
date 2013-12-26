'use strict';

/* Filters */

angular.module('shieldCommand.filters', [])

.filter('interpolate', ['version', function(version) {
    return function(text) {
      return String(text).replace(/\%VERSION\%/mg, version);
    }
  }])

.filter('byAgencyDispatcher', [function() {
	return function(alerts) {
		var filtered = [];
		for (var i = 0; i < alerts.length; i++) {
			if (alerts[i].agencyDispatcher && alerts[i].agencyDispatcher.indexOf(Javelin.activeAgencyUser.url) !== -1) {
				filtered.push(alerts[i]);
			}
		};
		return filtered;
	}
}]);
