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
	Javelin.activeCrimeTip = null;
	Javelin.activeCrimeTipUser = null;
	Javelin.lastCheckedCrimeTipsTimestamp = null;
	Javelin.spotCrimeURL = 'https://api.spotcrime.com/crimes.json';
	Javelin.spotCrimeDetailURL = 'https://api.spotcrime.com/crimes/<CDID>.json';
	Javelin.spotCrimeKey = null;

	// If jQuery or Zepto has been included, grab a reference to it.
	if (typeof($) !== "undefined") {
		Javelin.$ = $;
	}

	Javelin.GENDER_CHOICES = {
	    'M': 'Male',
	    'F': 'Female',
	};

	Javelin.ALERT_TYPE_CHOICES = {
	    'N': 'emergency',
        'E': 'call',
	    'C': 'chat',
	    'T': 'timer',
        'Y': 'yank',
        'S': 'static',
	};

	Javelin.HAIR_COLOR_CHOICES = {
	    'Y': 'Blonde',
	    'BR': 'Brown',
	    'BL': 'Black',
	    'R': 'Red',
	    'BA': 'Bald',
	    'GR': 'Gray',
	    'O': 'Other',
	};

	Javelin.RACE_CHOICES = {
	    'BA': 'Black/African Descent',
	    'WC': 'White/Caucasian',
	    'EI': 'East Indian',
	    'AS': 'Asian',
	    'LH': 'Latino/Hispanic',
	    'ME': 'Middle Eastern',
	    'PI': 'Pacific Islander',
	    'NA': 'Native American',
	    'O': 'Other',	    
	};

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
	};
	
	Javelin.CRIME_TYPE_CHOICES = {
	    'AB': 'Abuse',
	    'AS': 'Assault',
	    'CA': 'Car Accident',
	    'DI': 'Disturbance',
	    'DR': 'Drugs/Alcohol',
	    'H': 'Harassment',
	    'MH': 'Mental Health',
	    'O': 'Other',
		'RN': 'Repair Needed',
		'S': 'Suggestion',
		'SA': 'Suspicious Activity',
		'T': 'Theft',
		'V': 'Vandalism',
	};
	
	function getObjectProperty(obj, key)
	{
		return typeof obj[key] !== 'undefined' ? obj[key] : null;
	}
	
	function getCrimeTipIcon(reportType)
	{
		var crimeType = reportType ? reportType.toLowerCase().replace(/[\s\/]/g, '') : 'other';
		
		return '/media/static/shieldcommand/img/crimetip/alert_' + crimeType + '_icon.png';
	}

	function APIResponseObject(attributes) {
		this.parseIDFromURL = function(url) {
			var tokens = url.split('/');
			return tokens[tokens.length - 2];
		};

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
			this.profileImageURL = "/media/static/shieldcommand/img/NoPicture_Image.png"
		}
		return this;
	}

    function Region(attributes) {
		this.name = attributes.name;
		this.boundaries = attributes.boundaries;
		this.centerLatitude = attributes.center_latitude;
		this.centerLongitude = attributes.center_longitude;
		this.radius = attributes.radius;
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
		this.radius = attributes.agency_radius;
		this.defaultMapZoomLevel = attributes.default_map_zoom_level;
		this.alertCompletedMessage = attributes.alert_completed_message;
		this.requireDomainEmails = attributes.require_domain_emails;
		this.displayCommandAlert = attributes.display_command_alert;
		this.loopAlertSound = attributes.loop_alert_sound;
        this.spotCrimeDaysVisible = attributes.spot_crime_days_visible;
        this.theme = null;
        this.branding = null;
        this.noAlerts = attributes.no_alerts;

        if (attributes.region) {
            this.region = [];
            for (var i = 0; i < attributes.region.length; i++) {
		        newRegion = new Region(attributes.region[i]);
			    this.region.push(newRegion);
			}
        }

        if (!$.isEmptyObject(attributes.theme)) {
			this.theme = new Theme(attributes.theme);
        }
        if (!$.isEmptyObject(attributes.branding)) {
			this.branding = new Theme(attributes.branding);
        }
        return this;
	}

	function Alert(attributes) {
		APITimeStampedObject.call(this, attributes);
		this.agencyUser = attributes.agency_user;
		this.agencyUserMeta = null;
		this.agencyDispatcher = attributes.agency_dispatcher;
		this.agencyDispatcherName = attributes.agency_dispatcher_name;
		this.acceptedTime = attributes.accepted_time;
		this.completedTime = attributes.completed_time;
		this.disarmedTime = attributes.disarmed_time;
		this.pendingTime = attributes.pending_time;
		this.status = attributes.status;
		this.initiatedBy = Javelin.ALERT_TYPE_CHOICES[attributes.initiated_by];
		this.type = 'alert';
		this.location = null;
		this.geocodedAddress = '';
        this.staticDevice = attributes.static_device;
		this.staticDeviceMeta = null;
        this.callLength = attributes.call_length;

		if (!$.isEmptyObject(attributes.agency_user_meta)) {
			this.agencyUserMeta = new AgencyUser(attributes.agency_user_meta);
        }
        if (!$.isEmptyObject(attributes.static_device_meta)) {
			this.staticDeviceMeta = new StaticDevice(attributes.static_device_meta);
        }
        if (!$.isEmptyObject(attributes.latest_location)) {
			this.location = new AlertLocation(attributes.latest_location);
        }
        this.hasNewChatMessage = false;
		this.chatMessages = [];

		return this;
	}

	function AlertLocation(attributes) {
		APITimeStampedObject.call(this, attributes);
		this.accuracy = attributes.accuracy;
		this.altitude = attributes.altitude;
		this.latitude = attributes.latitude;
		this.type = 'alert';
		this.longitude = attributes.longitude;
		this.alertType = null;
		this.alertStatus = null;
		this.title = null;

		return this;
	}
	
	function CrimeTip(attributes) {
		APITimeStampedObject.call(this, attributes);
		this.distance = attributes.distance;
		this.body = attributes.body;
		this.reporter = attributes.reporter;
		this.reportType = getObjectProperty(Javelin.CRIME_TYPE_CHOICES, attributes.report_type);
		this.title = this.reportType;
		this.reportIcon = getCrimeTipIcon(this.reportType);
		this.imageURL = attributes.report_image_url;
		this.videoURL = attributes.report_video_url;
		this.audioURL = attributes.report_audio_url;
		this.latitude = attributes.report_latitude;
		this.longitude = attributes.report_longitude;
		this.geocodedAddress = null;
		this.type = 'crimeTip';
		this.anonymous = attributes.report_anonymous;
		this.accuracy = null;
		this.showPin = false;
		this.flaggedSpam = attributes.flagged_spam;
		this.flaggedBy = attributes.flagged_by_dispatcher;
		this.viewedTime = attributes.viewed_time;
		this.viewedBy = attributes.viewed_by;
		this.flaggedByName = null;
		this.viewedByName = null;
        this.dispatcherName = attributes.dispatcher_name;
		
		return this;
	}
	
	function SpotCrime(attributes) {
		this.object_id = attributes.cdid;
		this.reportType = attributes.type;
		this.title = attributes.type;
		this.latitude = attributes.lat;
		this.longitude = attributes.lon;
		this.creationDate = attributes.date;
		this.link = attributes.link;
		this.address = attributes.address;
		this.description = attributes.description ? attributes.description : null;
		this.type = 'spotCrime';
		
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

    function StaticDevice(attributes) {
        this.url = attributes.url;
		this.uuid = attributes.uuid;
		this.type = attributes.type;
		this.description = attributes.description;
		this.agency = attributes.agency;
		this.latitude = attributes.latitude;
        this.longitude = attributes.longitude;
        this.user = attributes.user;
		return this;
	}

    function Theme(attributes) {
		this.name = attributes.name;
		this.primaryColor = attributes.primary_color;
		this.secondaryColor = attributes.secondary_color;
		this.alternateColor = attributes.alternate_color;
		this.logo = attributes.logo;
        this.alternateLogo = attributes.alternate_logo;
        this.smallLogo = attributes.small_logo;
        this.shieldCommandLogo = attributes.shield_command_logo;
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
	
	function createPastTimestamp(past)
	{
		return Math.round(new Date().getTime() / 1000) - past;
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

        Javelin.client.add('region', {url: 'region'});

		Javelin.client.add('alerts');
        Javelin.client.alerts.add('complete');
		Javelin.client.alerts.add('send_message');
		Javelin.client.alerts.add('messages');
		Javelin.client.alerts.add('messages_since');

		Javelin.client.add('alertlocations', {url: 'alert-locations'});
		Javelin.client.add('users');
		Javelin.client.add('userprofiles', {url: 'user-profiles'});
		Javelin.client.add('crimetips', {url: 'social-crime-reports'});
        Javelin.client.crimetips.add('mark_viewed');

		Javelin.getAgency(agencyID, function(agency) {
			Javelin.activeAgency = agency;
		});
	};

	Javelin.setActiveAgencyUserAttributes = function(attributes) {
		Javelin.activeAgencyUser = new AgencyUser(attributes);
	};

	Javelin.setActiveAlert = function(alert) {
		Javelin.activeAlert = alert;
	};
	
	Javelin.setActiveCrimeTip = function(crimeTip) {
		Javelin.activeCrimeTip = crimeTip;
	};
	
	Javelin.setActiveCrimeTipUser = function(user) {
		Javelin.activeCrimeTipUser = user;
	};

	Javelin.claimAlertForActiveUser = function(alertID, callback) {
		var request = Javelin.client.alerts.patch(alertID, {
			agency_dispatcher: Javelin.activeAgencyUser.url,
			status: 'A'
		});
		request.done(function(data) {
			callback(data);
		});
	};

	Javelin.markAlertAsCompleted = function(alert, callback) {
		var request = Javelin.client.alerts.complete.create(alert.object_id);
		request.done(function(data) {
			callback(data);
		})
	};

	Javelin.markAlertAsPending = function(alertID, callback) {
		var request = Javelin.client.alerts.patch(alertID, {
			status: 'P'
		});
		request.done(function(data) {
			callback(data);
		})
	};

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
	};

	Javelin.getAgency = function(agencyID, callback) {
		var request = Javelin.client.agencies.read(agencyID);
		request.done(function(data) {
			var retrievedAgency = new Agency(data);
			callback(retrievedAgency);
		});
	};

	Javelin.getUser = function(userID, callback) {
		var request = Javelin.client.users.read(userID);
		request.done(function(data) {
			if (data) {
					callback(new AgencyUser(data));
			}
			else {
				callback(null);
			}
		});
	};
	
	Javelin.getUserProfileForUser = function(userID, callback) {
		var request = Javelin.client.userprofiles.read({user: userID});
		request.done(function(data) {
			if (data.results && data.results.length > 0) {
				callback(new AgencyUserProfile(data.results[0]));
			}
			else {
				callback(null);
			}
		});
	};

    Javelin.getRegions = function(agencyID, callback) {
		var request = Javelin.client.region.read({agency: agencyID});
		request.done(function(data) {
			if (data.results && data.results.length > 0) {
                var allRegions = [];
                for (var i = 0; i < data.results.length; i++) {
				    newRegion = new Region(data.results[i]);
				    allRegions.push(newRegion);
			    }
				callback(allRegions);
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
            if (data.results) {
                for (var i = data.results.length - 1; i >= 0; i--) {
				    newAgency = new Agency(data.results[i]);
				    retrievedAgencies.push(newAgency);
			    }
            }
			callback(retrievedAgencies);
		});
	};

	Javelin.getAlerts = function(options, callback) {
		var defaultOptions = { agency: Javelin.agencyID };
		var request = Javelin.client.alerts.read(params=Javelin.$.extend(defaultOptions, options));
		request.done(function(data) {
			var retrievedAlerts = [];
            var latestDate = Javelin.lastCheckedAlertsTimestamp ||
                createTimestampFromDate(new Date("March 25, 1981 11:33:00"));

			if (data.results) {
                for (var i = 0; i < data.results.length; i++) {
                    newAlert = new Alert(data.results[i]);
                    retrievedAlerts.push(newAlert);
                    newAlertDate = createTimestampFromDate(new Date(newAlert.lastModified));
                    if (newAlertDate > latestDate) {
                        latestDate = newAlertDate;
                    }
                }
            }
			if (latestDate > Javelin.lastCheckedAlertsTimestamp) {
				Javelin.lastCheckedAlertsTimestamp = latestDate;
			}

			callback(retrievedAlerts);
		})
	};

	Javelin.getAlertsModifiedSinceLastCheck = function(callback) {
		Javelin.getAlerts({
			modified_since: Javelin.lastCheckedAlertsTimestamp,
		}, callback);
	};

	Javelin.getAcceptedAlerts = function(dispatcherID, callback) {
		Javelin.getAlerts({
			status: "A",
			agency_dispatcher: dispatcherID,
		}, callback);
	};

	Javelin.getDisarmedAlerts = function(callback) {
		Javelin.getAlerts({
			status: "D",
		}, callback);
	};

	Javelin.getNewAlerts = function(callback) {
		Javelin.getAlerts({
			status: "N",
		}, callback);
	};

	Javelin.getPendingAlerts = function(callback) {
		Javelin.getAlerts({
			status: "P",
		}, callback);
	};

	Javelin.getLatestLocationForAlert = function(alertID, callback) {
		var request = Javelin.client.alerts.read(alertID);
		request.done(function(data) {
			if (data && data.locations.length > 0) {
				latestLocation = new AlertLocation(data.locations[0]);
				callback(latestLocation);
			}
			else {
				callback(null);
			}
		})
	};

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
	};

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
	};

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
		request.fail(function(data) {
			callback(false);
		});
	};

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
		request.fail(function(data) {
			callback(false);
		});
	};
	
	Javelin.getCrimeTips = function(options, callback) {
		if ( ! Javelin.activeAgency) {
 			callback(null);
 		}

 		var agency = Javelin.activeAgency;
		var defaultOptions = { latitude: agency.agencyCenterLatitude, longitude: agency.agencyCenterLongitude, distance_within: agency.radius };
        var allParameters = [];
        var regions = agency.region;

        if (regions.length > 0)
            for (var i = regions.length - 1; i >= 0; i--) {
                allParameters.push({ latitude: regions[i].centerLatitude, longitude: regions[i].centerLongitude, distance_within: regions[i].radius });
            }
        else {
            allParameters.push(defaultOptions);
        }

        for (var i = allParameters.length - 1; i >= 0; i--) {
           var request = Javelin.client.crimetips.read(params=Javelin.$.extend(allParameters[i], options));
 		    request.done(function(data) {

                var retrievedCrimeTips = [];
                var latestDate = Javelin.lastCheckedCrimeTipsTimestamp || createTimestampFromDate(new Date("March 25, 1981 11:33:00"));
                if (data.results) {
                    for (var i = data.results.length - 1; i >= 0; i--) {
                        var newCrimeTip = new CrimeTip(data.results[i]);
                        var past24 = createPastTimestamp(24 * 3600);
                        var newCrimeTipDate = createTimestampFromDate(new Date(newCrimeTip.lastModified));

                        if (newCrimeTipDate >= past24 && newCrimeTip.flaggedSpam == false && newCrimeTip.viewedTime == null) {
                            newCrimeTip.showPin = true;
                        }
                        retrievedCrimeTips.push(newCrimeTip);

                        if (newCrimeTipDate > latestDate) {
                            latestDate = newCrimeTipDate;
                        }
                    }
                    if (latestDate > Javelin.lastCheckedCrimeTipsTimestamp) {
                        Javelin.lastCheckedCrimeTipsTimestamp = latestDate;
                    }
                }
                callback(retrievedCrimeTips);
            })
        }

 	};
	
	Javelin.getSpotCrimes = function(callback) {
		if ( ! Javelin.activeAgency || ! Javelin.spotCrimeKey)
 		{
 			callback(null);
 			return;
 		}

 		var agency = Javelin.activeAgency;
		var date = new Date();
		date.setDate(date.getDate() - agency.spotCrimeDaysVisible);
        var retrievedSpotCrimes = [];
		Javelin.$.ajax({
			type: 'GET',
			url: Javelin.spotCrimeURL,
			crossDomain: true,
			async: false,
			dataType: 'jsonp',
			jsonp: 'callback',
			data: {
				key: Javelin.spotCrimeKey,
				lat: agency.agencyCenterLatitude,
				lon: agency.agencyCenterLongitude,
				radius:.25,
				since: date.toISOString().slice(0, 10),
				max_records: 500

			},
			success: function(response) {
				if (response.crimes)
				{
					for (var i = 0; i < response.crimes.length; i++)
					{
						retrievedSpotCrimes.push(new SpotCrime(response.crimes[i]));
					}
					
					callback(retrievedSpotCrimes);
				}
				else
				{
					callback(null);
					console.log('spotcrime api error');
				}
			}
		});
 	};
	
	Javelin.getSpotCrime = function(id, callback) {
		Javelin.$.ajax({
			type: 'GET',
			url: Javelin.spotCrimeDetailURL.replace('<CDID>', id),
			//crossDomain: true,
			async: false,
			dataType: 'json',
			//jsonp: 'callback',
			data: {
				key: Javelin.spotCrimeKey
			},
			success: function(response) {
				if (response)
				{
					callback(new SpotCrime(response));
				}
				else
				{
					callback(null);
					console.log('spotcrime api error');
				}
			}
		});
 	};
	
	Javelin.loadInitialCrimeTips = function(callback) {
		//var now = getTimestamp(milliseconds=true);
		//var then = Number(new Date(now - (24 * 60 * 60)));
		Javelin.getCrimeTips({
			//modified_since: then,
			page_size: 100,
		}, callback);		
	};

	Javelin.updateCrimeTips = function(callback) {
		Javelin.getCrimeTipsModifiedSinceLastCheck(function(updatedCrimeTips) {
			callback(updatedCrimeTips);
		});
	};
	
	Javelin.getCrimeTipsModifiedSinceLastCheck = function(callback) {
		Javelin.getCrimeTips({
			modified_since: Javelin.lastCheckedCrimeTipsTimestamp,
			page_size: 100,
		}, callback);
	};
	
	Javelin.markCrimeTipViewed = function(crimeTip, callback) {

        var request = Javelin.client.crimetips.mark_viewed.create(crimeTip.object_id);
		request.done(function(data) {
			if (request.status == 200) {
				callback(data);
			}
			else {
				callback(data);
			}
		});
		request.fail(function(data) {
			callback(data);
		});


//        send_mass_alert
//		var now = new Date();
//		var old = new Date("March 25, 1981 11:33:00");
//		var request = Javelin.client.crimetips.patch(crimeTip.object_id, {
//			viewed_time: now.toISOString(),
//			viewed_by: Javelin.activeAgencyUser.url,
//			last_modified: old.toISOString(),
//		});
//		request.done(function(data) {
//			callback(data);
//		})
	};
	
	Javelin.markCrimeTipSpam = function(crimeTip, callback) {
		var old = new Date("March 25, 1981 11:33:00");
		var request = Javelin.client.crimetips.patch(crimeTip.object_id, {
			flagged_spam: true,
			flagged_by_dispatcher: Javelin.activeAgencyUser.url,
			last_modified: old.toISOString(),
		});
		request.done(function(data) {
			callback(data);
		})
	}

}(this));