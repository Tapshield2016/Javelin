(function(root) {
    root.Javelin = root.Javelin || {};
    root.Javelin.VERSION = "0.1";
}(this));


(function(root) {
    root.Javelin = root.Javelin || {};

    var Javelin = root.Javelin;
    Javelin.alerts = [];
    Javelin.activeAgency = null;
    Javelin.activeAgencyUser = null;    
    Javelin.activeAlert = null;
    Javelin.activeAlertTarget = null;
    Javelin.lastCheckedAlertsTimestamp = null;

	// If jQuery or Zepto has been included, grab a reference to it.
	if (typeof($) !== "undefined") {
		Javelin.$ = $;
	}

	Javelin.GENDER_CHOICES = {
	    'M': 'Male',
	    'F': 'Female',
	}

	Javelin.ALERT_TYPE_CHOICES = {
	    'E': 'emergency',
	    'C': 'chat',
	    'T': 'timer',
	}

	Javelin.HAIR_COLOR_CHOICES = {
	    'Y': 'Blonde',
	    'BR': 'Brown',
	    'BL': 'Black',
	    'R': 'Red',
	    'BA': 'Bald',
	    'GR': 'Gray',
	}

	Javelin.RACE_CHOICES = {
	    'BA': 'Black/African Descent',
	    'WC': 'White/Caucasian',
	    'EI': 'East Indian',
	    'AS': 'Asian',
	    'LH': 'Latino/Hispanic',
	    'ME': 'Middle Eastern',
	    'PI': 'Pacific Islander',
	    'NA': 'Native American',
	}

	Javelin.RELATIONSHIP_CHOICES = {
	    'F': 'Father',
	    'M': 'Mother',
	    'S': 'Spouse',
	    'BF': 'Boyfriend',
	    'GF': 'Girlfriend',
	    'B': 'Brother',
	    'SI': 'Sister',
	    'FR': 'Friend',
	    'O': 'Other',
	}


	function APIResponseObject(attributes) {
		this.parseIDFromURL = function(url) {
			var tokens = url.split('/')
			return tokens[tokens.length - 2];
		}

		this.url = attributes.url;
		this.object_id = this.parseIDFromURL(attributes.url);

		return this;
	}

	function APITimeStampedObject(attributes) {
		APIResponseObject.call(this, attributes);
		this.creationDate = attributes.creation_date;
		this.lastModified = attributes.last_modified;		
		return this;
	}

	function AgencyUser(attributes) {
		APIResponseObject.call(this, attributes);
		this.url = attributes.url;
		this.username = attributes.username;
		this.email = attributes.email;
		this.agencyURL = attributes.agency;
		this.phoneNumber = attributes.phone_number;
		this.disarmCode = attributes.disarm_code;
		this.firstName = attributes.first_name;
		this.lastName = attributes.last_name;

		this.getFullName = function() {
			return this.firstName + " " + this.lastName;
		};
	}

	function AgencyUserProfile(attributes) {
		APIResponseObject.call(this, attributes);
		this.birthday = attributes.birthday;
		this.address = attributes.address;
		this.hairColor = Javelin.HAIR_COLOR_CHOICES[attributes.hair_color];
		this.gender = Javelin.GENDER_CHOICES[attributes.gender];
		this.race = Javelin.RACE_CHOICES[attributes.race];
		this.height = attributes.height;
		this.weight = attributes.weight;
		this.knownAllergies = attributes.known_allergies;
		this.medications = attributes.medications;
		this.emergencyContactFirstName = attributes.emergency_contact_first_name;
		this.emergencyContactLastName = attributes.emergency_contact_last_name;
		this.emergencyContactPhoneNumber = attributes.emergency_contact_phone_number;
		this.emergencyContactRelationship = Javelin.RELATIONSHIP_CHOICES[attributes.emergency_contact_relationship];
		if (attributes.profile_image_url) {
			this.profileImageURL = attributes.profile_image_url;
		}
		else {
			this.profileImageURL = "/media/static/shieldcommand/img/default-avatar.png"
		}
		return this;
	}

	function Agency(attributes) {
		APITimeStampedObject.call(this, attributes);
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
		this.requireDomainEmails = attributes.require_domain_emails;
		this.displayCommandAlert = attributes.display_command_alert;
		this.loopAlertSound = attributes.loop_alert_sound;
		return this;
	}

	function Alert(attributes) {
		APITimeStampedObject.call(this, attributes);
		this.agencyUser = attributes.agency_user;
		this.agencyUserMeta = null;
		this.agencyDispatcher = attributes.agency_dispatcher;
		this.acceptedTime = attributes.accepted_time;
		this.completedTime = attributes.completed_time;
		this.disarmedTime = attributes.disarmed_time;
		this.pendingTime = attributes.pending_time;
		this.status = attributes.status;
		this.initiatedBy = Javelin.ALERT_TYPE_CHOICES[attributes.initiated_by];
		this.location = null;
		this.geocodedAddress = '';

		if (!$.isEmptyObject(attributes.agency_user_meta)) {
			this.agencyUserMeta = new AgencyUser(attributes.agency_user_meta);
		};

		if (!$.isEmptyObject(attributes.latest_location)) {
			this.location = new AlertLocation(attributes.latest_location);
		};

		this.hasNewChatMessage = false;
		this.chatMessages = [];
		
		return this;
	}

	function AlertLocation(attributes) {
		APITimeStampedObject.call(this, attributes);
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

	function createTimestampFromDate(dateObj, seconds) {
		seconds = seconds || true;
		timestamp = Number(dateObj);
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
			verbs: {
				'create': 'POST',
				'read': 'GET',
				'update': 'PUT',
				'patch': 'PATCH',
				'destroy': 'DELETE'
			}
		});

		Javelin.client.add('agencies');
		Javelin.client.agencies.add('send_mass_alert');

		Javelin.client.add('alerts');
		Javelin.client.alerts.add('send_message');
		Javelin.client.alerts.add('messages');
		Javelin.client.alerts.add('messages_since');

		Javelin.client.add('alertlocations', {url: 'alert-locations'});
		Javelin.client.add('users');
		Javelin.client.add('userprofiles', {url: 'user-profiles'});

		Javelin.getAgency(agencyID, function(agency) {
			Javelin.activeAgency = agency;
		});
	};

	Javelin.setActiveAgencyUserAttributes = function(attributes) {
		Javelin.activeAgencyUser = new AgencyUser(attributes);
	}

	Javelin.setActiveAlert = function(alert) {
		Javelin.activeAlert = alert;
	}

	Javelin.claimAlertForActiveUser = function(alertID, callback) {
		var request = Javelin.client.alerts.patch(alertID, {
			agency_dispatcher: Javelin.activeAgencyUser.url,
			status: 'A'
		});
		request.done(function(data) {
			callback(data);
		});
	}

	Javelin.markAlertAsCompleted = function(alert, callback) {
		var request = Javelin.client.alerts.patch(alert.object_id, {
			status: 'C'
		});
		request.done(function(data) {
			callback(data);
			Javelin.sendChatMessageForAlert(alert, Javelin.activeAgency.alertCompletedMessage, function(success) {
				console.log(success);
			})
		})
	}

	Javelin.markAlertAsPending = function(alertID, callback) {
		var request = Javelin.client.alerts.patch(alertID, {
			status: 'P',
		});
		request.done(function(data) {
			callback(data);
		})
	}

	Javelin.loadInitialAlerts = function(callback) {
		var now = getTimestamp(milliseconds=true);
		var then = Number(new Date(now - (24 * 60 * 60)));
		Javelin.getAlerts({
			modified_since: then,
			page_size: 15,
		}, callback);		
	};

	Javelin.updateAlerts = function(callback) {
		Javelin.getAlertsModifiedSinceLastCheck(function(updatedAlerts) {
			callback(updatedAlerts);
		});
	}

	Javelin.getAgency = function(agencyID, callback) {
		var request = Javelin.client.agencies.read(agencyID);
		request.done(function(data) {
			var retrievedAgency = new Agency(data);
			callback(retrievedAgency);
		});
	};

	Javelin.getUserProfileForUser = function(userID, callback) {
		var request = Javelin.client.userprofiles.read({user: userID});
		request.done(function(data) {
			if (data['results'].length > 0) {
				callback(new AgencyUserProfile(data['results'][0]));
			}
			else {
				callback(null);
			}
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
			var retrievedAlerts = [];
			var latestDate = Javelin.lastCheckedAlertsTimestamp || createTimestampFromDate(new Date("March 25, 1981 11:33:00"));
			for (var i = data.results.length - 1; i >= 0; i--) {
				newAlert = new Alert(data.results[i]);
				retrievedAlerts.push(newAlert);
				newAlertDate = createTimestampFromDate(new Date(newAlert.lastModified));
				if (newAlertDate > latestDate) {
					latestDate = newAlertDate;
				}
			}
			if (latestDate > Javelin.lastCheckedAlertsTimestamp) {
				Javelin.lastCheckedAlertsTimestamp = latestDate;
			};
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

	Javelin.getAllChatMessagesForAlert = function(alert, callback) {
		if (!alert) {
			callback(null);
		}
		else {
			var request = Javelin.client.alerts.messages.read(alert.object_id);
			request.done(function(data) {
				var chatMessages = [];
				var latestTimestamp = createTimestampFromDate(new Date("March 25, 1981 11:33:00"));
				for (var i = 0; i < data.length; i++) {
					newChatMessage = new ChatMessage(data[i]);
					chatMessages.push(newChatMessage);
					if (newChatMessage.timestamp > latestTimestamp) {
						latestTimestamp = newChatMessage.timestamp;
					}
				}

				callback(chatMessages, latestTimestamp);
			});
		}
	}

	Javelin.getAllChatMessagesForAlertSinceLastChecked = function(alert, since_timestamp, callback) {
		if (!alert) {
			callback(null);
		}
		else {
			var request = Javelin.client.alerts.messages_since.read(alert.object_id, params={timestamp: since_timestamp});
			request.done(function(data) {
				var chatMessages = [];
				var latestTimestamp = createTimestampFromDate(new Date("March 25, 1981 11:33:00"));		
				for (var i = 0; i < data.length; i++) {
					newChatMessage = new ChatMessage(data[i]);
					chatMessages.push(newChatMessage);
					if (newChatMessage.timestamp > latestTimestamp) {
						latestTimestamp = newChatMessage.timestamp;
					}
				}

				callback(chatMessages, latestTimestamp);
			});
		}
	}

	Javelin.sendChatMessageForAlert = function(alert, message, callback) {
		var request = Javelin.client.alerts.send_message.create(alert.object_id, {message: message});
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