(function(root) {
    root.Javelin = root.Javelin || {};
    root.Javelin.VERSION = "0.1";
}(this));


(function(root) {
    root.Javelin = root.Javelin || {};

    var Javelin = root.Javelin;
    Javelin.alerts = [];
    Javelin.activeAgency = null;
    Javelin.activeAlert = null;
    Javelin.activeAlertTarget = null;
    Javelin.lastCheckedAlertsTimestamp = getTimestamp();
    Javelin.lastCheckedMessagesTimestamp = getTimestamp();

	// If jQuery or Zepto has been included, grab a reference to it.
	if (typeof($) !== "undefined") {
		Javelin.$ = $;
	}

	function APIResponseObject(attributes) {
		this.url = attributes.url;
		this.creationDate = attributes.creation_date;
		this.lastModified = attributes.last_modified;
		return this;
	}

	function Agency(attributes) {
		APIResponseObject.call(this, attributes);
		this.name = attributes.name;
		this.domain = attributes.domain;
		this.agencyPointOfContact = attributes.agency_point_of_contact;
		this.dispatcherPhoneNumber = attributes.dispatcher_phone_number;
		this.dispatcherSecondaryNumber = attributes.dispatcher_secondary_phone_number;
		this.dispatcherScheduleStart = attributes.dispatcher_schedule_start;
		this.dispatcherScheduleEnd = attributes.dispatcher_schedule_end;		
		this.agencyBoundaries = attributes.agency_boundaries;
		this.agencyCenterLatitude = attributes.agency_center_latitude;
		this.agencyCenterLongitude = attributes.agency_center_longitude;
		this.defaultMapZoomLevel = attributes.default_map_zoom_level;
		this.alertCompletedMessage = attributes.alert_completed_message;
		return this;
	}

	function Alert(attributes) {
		APIResponseObject.call(this, attributes);
		this.agencyUser = attributes.agency_user;
		this.agencyDispatcher = attributes.agency_dispatcher;
		this.acceptedTime = attributes.accepted_time;
		this.completedTime = attributes.completed_time;
		this.disarmedTime = attributes.disarmed_time;
		this.pendingTime = attributes.pending_time;
		this.status = attributes.status;
		this.initiatedBy = attributes.initiated_by;
		return this;
	}

	function AlertLocation(attributes) {
		APIResponseObject.call(this, attributes);
		this.accuracy = attributes.accuracy;
		this.altitude = attributes.altitude;
		this.latitude = attributes.latitude;
		this.longitude = attributes.longitude;
		return this;
	}

	function ChatMessage(attributes) {
		this.alertID = attributes.alert_id;
		this.timestamp = attributes.timestamp;
		this.message = attributes.message;
		this.messageID = attributes.message_id;
		this.senderID = attributes.sender_id;
		return this;
	}

	function getTimestamp(seconds) {
		seconds = seconds || true;
		timestamp = Number(new Date());
		if (seconds) {
			timestamp /= 1000;
		}
		return timestamp;
	}

	Javelin.initialize = function(serverURL, agencyID, apiToken) {
		Javelin._initialize(serverURL, agencyID, apiToken);
	};

	Javelin._initialize = function(serverURL, agencyID, apiToken) {
		Javelin.serverURL = serverURL;
		Javelin.agencyID = agencyID;
		Javelin.apiToken = apiToken;

		Javelin.client = new Javelin.$.RestClient(Javelin.serverURL, {
			ajax: {headers: {'Authorization': "Token " + Javelin.apiToken}},
		});

		Javelin.client.add('agencies');
		Javelin.client.agencies.add('send_mass_alert');

		Javelin.client.add('alerts');
		Javelin.client.alerts.add('send_message');
		Javelin.client.alerts.add('messages');
		Javelin.client.alerts.add('messages_since');

		Javelin.client.add('alert-locations');

		// Javelin.loadInitialAlerts(function(alerts) {
		// 	Javelin.alerts = alerts;
		// 	console.log(Javelin.alerts.length);
		// 	setTimeout(Javelin.updateAlerts, 3000);
		// });
	};

	Javelin.loadInitialAlerts = function(callback) {
		var now = getTimestamp(milliseconds=true);
		var then = Number(new Date(now - (24 * 60 * 60)));
		Javelin.getAlerts({
			modified_since: then,
			page_size: 5,
		}, callback);		
	};

	Javelin.updateAlerts = function() {
		Javelin.getAlertsModifiedSinceLastCheck(function(updatedAlerts) {
			if (updatedAlerts.length == 0) {
				console.log("No updates");
			}
			else {
				for (var i = 0; i < updatedAlerts.length; i++) {
					for (var j = 0; j < Javelin.alerts.length; j++) {
						if (Javelin.alerts[j].url === updatedAlerts[i].url) {
							for (var key in updatedAlerts[i]) {
								Javelin.alerts[j][key] = updatedAlerts[i][key];
								console.log("Replaced value for " + key + " with " + updatedAlerts[i][key]);
							}
						}
					};
				};
			}
			setTimeout(Javelin.updateAlerts, 3000);
		});
	}

	Javelin.getAgency = function(agencyID, callback) {
		var request = Javelin.client.agencies.read(agencyID);
		request.done(function(data) {
			var retrievedAgency = new Agency(data);
			callback(retrievedAgency);
		});
	};

	Javelin.getAgencies = function(callback) {
		var request = Javelin.client.agencies.read();
		request.done(function (data) {
			var retrievedAgencies = [];
			for (var i = data.results.length - 1; i >= 0; i--) {
				newAgency = new Agency(data.results[i]);
				retrievedAgencies.push(newAgency);
			}
			callback(retrievedAgencies);
		});
	};

	Javelin.getAlerts = function(options, callback) {
		var defaultOptions = { agency: Javelin.agencyID };
		var request = Javelin.client.alerts.read(params=Javelin.$.extend(defaultOptions, options));
		request.done(function(data) {
			Javelin.lastCheckedAlertsTimestamp = getTimestamp();
			var retrievedAlerts = [];
			for (var i = data.results.length - 1; i >= 0; i--) {
				newAlert = new Alert(data.results[i]);
				retrievedAlerts.push(newAlert);
			}
			callback(retrievedAlerts);
		})
	}

	Javelin.getAlertsModifiedSinceLastCheck = function(callback) {
		Javelin.getAlerts({
			modified_since: Javelin.lastCheckedAlertsTimestamp,
		}, callback);
	}

	Javelin.getAcceptedAlerts = function(dispatcherID, callback) {
		Javelin.getAlerts({
			status: "A",
			agency_dispatcher: dispatcherID,
		}, callback);
	}

	Javelin.getDisarmedAlerts = function(callback) {
		Javelin.getAlerts({
			status: "D",
		}, callback);
	}

	Javelin.getNewAlerts = function(callback) {
		Javelin.getAlerts({
			status: "N",
		}, callback);
	}

	Javelin.getPendingAlerts = function(callback) {
		Javelin.getAlerts({
			status: "P",
		}, callback);
	}

	Javelin.getLatestLocationForAlert = function(alertID, callback) {
		var request = Javelin.client.alerts.read(alertID);
		request.done(function(data) {
			if (data && data['locations'].length > 0) {
				latestLocation = new AlertLocation(data['locations'][0]);
				callback(latestLocation);
			}
			else {
				callback(null);
			}
		})
	}

	Javelin.getAllChatMessagesForAlert = function(alertID, callback) {
		var request = Javelin.client.alerts.messages.read(alertID);
		request.done(function(data) {
			Javelin.lastCheckedMessagesTimestamp = getTimestamp();
			var chatMessages = [];
			for (var i = 0; i < data.length; i++) {
				newChatMessage = new ChatMessage(data[i]);
				chatMessages.push(newChatMessage);
			};
			callback(chatMessages);
		});
	}

	Javelin.getAllChatMessagesForAlertSinceTime = function(alertID, timestamp, callback) {
		var request = Javelin.client.alerts.messages_since.read(alertID, params={timestamp: timestamp});
		request.done(function(data) {
			Javelin.lastCheckedMessagesTimestamp = getTimestamp();			
			var chatMessages = [];
			for (var i = 0; i < data.length; i++) {
				newChatMessage = new ChatMessage(data[i]);
				chatMessages.push(newChatMessage);
			};
			callback(chatMessages);
		});
	}

	Javelin.sendChatMessageForAlert = function(alertID, message, callback) {
		var request = Javelin.client.alerts.send_message.create(alertID, {message: message});
		request.done(function(data) {
			if (request.status == 200) {
				callback(true);
			}
			else {
				callback(false);
			}
		});
	}

	Javelin.sendMassAlert = function(message, callback) {
		var request = Javelin.client.agencies.send_mass_alert.create(Javelin.agencyID, {message: message});
		request.done(function(data) {
			if (request.status == 200) {
				callback(true);
			}
			else {
				callback(false);
			}
		});
	}

}(this));