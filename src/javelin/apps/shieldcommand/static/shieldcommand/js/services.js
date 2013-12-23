'use strict';

/* Services */


// Demonstrate how to register services
// In this case it is a simple value service.
angular.module('shieldCommand.services', [])

.value('version', '1.0')

.factory('alertService', [function () {

	this.loadInitialAlerts = function (callback) {
		Javelin.loadInitialAlerts(function(initialAlerts) {
			callback(initialAlerts);
		});
	};

	this.getUpdatedAlerts = function (existingAlerts, callback) {
		Javelin.updateAlerts(function(updatedAlerts) {

			for (var i = 0; i < updatedAlerts.length; i++) {
				var foundAlert = false;
				for (var j = 0; j < existingAlerts.length; j++) {
					if (existingAlerts[j].url === updatedAlerts[i].url) {
						foundAlert = true;
						for (var key in updatedAlerts[i]) {
							existingAlerts[j][key] = updatedAlerts[i][key];
						}
						break;
					}
				}
				if (!foundAlert) {
					existingAlerts.push(updatedAlerts[i]);
				};
			};

			callback(existingAlerts);
		});
	}

	return {
		loadInitialAlerts: this.loadInitialAlerts,
		getUpdatedAlerts: this.getUpdatedAlerts,
	}
}]);