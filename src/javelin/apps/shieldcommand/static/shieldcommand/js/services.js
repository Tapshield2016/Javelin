'use strict';

/* Services */


// Demonstrate how to register services
// In this case it is a simple value service.
angular.module('shieldCommand.services', [])

.value('version', '1.0')

.factory('alertService', [function () {
	var alerts = [];

	this.loadInitialAlerts = function (callback) {
		Javelin.loadInitialAlerts(function(initialAlerts) {
			alerts = initialAlerts;
			callback(initialAlerts);
		});
	};

	return {
		alerts: alerts,
		loadInitialAlerts: this.loadInitialAlerts,
	}
}]);