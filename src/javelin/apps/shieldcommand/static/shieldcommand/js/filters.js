'use strict';

/* Filters */

angular.module('shieldCommand.filters', [])

.filter('interpolate', ['version', function(version) {
    return function(text) {
      return String(text).replace(/\%VERSION\%/mg, version);
    }
  }])

.filter('myAlerts', function() {
	return function(input, filterKey, filterVal) {
		
	}
});
