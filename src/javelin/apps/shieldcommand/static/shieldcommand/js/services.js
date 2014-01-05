'use strict';

/* Services */


// Demonstrate how to register services
// In this case it is a simple value service.
angular.module('shieldCommand.services', [])

.value('version', '1.0')

.factory('alertService', [function () {
	var activeAlert = null;

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

	this.setActiveAlert = function(alert) {
		this.activeAlert = alert;
		Javelin.setActiveAlert(alert);
	}

	this.claimAlertForActiveUser = function(alert, callback) {
		Javelin.claimAlertForActiveUser(alert.object_id, function(data) {
			callback(data);
		});
	}

	this.markActiveAlertAsCompleted = function(callback) {
		Javelin.markAlertAsCompleted(this.activeAlert, function(data) {
			callback(data);
		});
	}

	this.markActiveAlertAsPending = function(callback) {
		Javelin.markAlertAsPending(this.activeAlert.object_id, function(data) {
			callback(data);
		});
	}

	this.getUserProfileForActiveAlert = function(callback) {
		if (this.activeAlert) {
			Javelin.getUserProfileForUser(this.activeAlert.agencyUserMeta.object_id, function(profile) {
				callback(profile);
			});
		}
		else {
			if (callback) {
				callback(null);
			}
		}
	}

	this.sendChatMessageForActiveAlert = function(message, callback) {
		Javelin.sendChatMessageForAlert(this.activeAlert, message, function(success) {
			callback(success);
		});
	}

	this.getAllChatMessagesForActiveAlert = function(callback) {
		Javelin.getAllChatMessagesForAlert(this.activeAlert, function(messages, latestTimestamp) {
			callback(messages, latestTimestamp);
		})
	}

	this.getNewChatMessagesForActiveAlert = function(since_timestamp, callback) {
		Javelin.getAllChatMessagesForAlertSinceLastChecked(this.activeAlert, since_timestamp, function(messages, latestTimestamp) {
			callback(messages, latestTimestamp);
		})
	}

	this.activeAgency = function() {
		return Javelin.activeAgency;
	}

	this.sendMassAlert = function(message, callback) {
		Javelin.sendMassAlert(message, function(success) {
			callback(success);
		});
	}

	return {
		activeAlert: this.activeAlert,
		loadInitialAlerts: this.loadInitialAlerts,
		getUpdatedAlerts: this.getUpdatedAlerts,
		claimAlertForActiveUser: this.claimAlertForActiveUser,
		markActiveAlertAsCompleted: this.markActiveAlertAsCompleted,
		markActiveAlertAsPending: this.markActiveAlertAsPending,		
		setActiveAlert: this.setActiveAlert,
		getUserProfileForActiveAlert: this.getUserProfileForActiveAlert,
		sendChatMessageForActiveAlert: this.sendChatMessageForActiveAlert,
		getAllChatMessagesForActiveAlert: this.getAllChatMessagesForActiveAlert,
		getNewChatMessagesForActiveAlert: this.getNewChatMessagesForActiveAlert,
		activeAgency: this.activeAgency,
		sendMassAlert: this.sendMassAlert,
	}
}]);