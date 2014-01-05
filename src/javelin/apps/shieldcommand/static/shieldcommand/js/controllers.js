'use strict';

/* Controllers */

angular.module('shieldCommand.controllers', [])

.controller('CommandAlertController', ['$scope', 'alertService', function($scope, alertService) {

	$scope.sendCommandAlertMessage = function() {
		alertService.sendMassAlert($scope.message, function(success) {
			if (success) {
				$scope.dismiss();
				$scope.message = '';
			}
			else {

			}
		});
	}

}])

.controller('UserProfileController', ['$rootScope', '$scope', 'alertService', function($rootScope, $scope, alertService) {

	$scope.currentProfile = null;
	$scope.activeAlert = null;
	$scope.isProfileVisible = false;
	$rootScope.profileIsOpen = false;

	$scope.toggle = function() {
		$scope.isProfileVisible = !$scope.isProfileVisible;
		if ($scope.isProfileVisible) {
			$rootScope.$broadcast('profileWasOpened');
			$rootScope.profileIsOpen = true;
		}
		else {
			$rootScope.$broadcast('profileWasClosed');
			$rootScope.profileIsOpen = false;
		}
	}

	$scope.$on('toggleProfile', function() {
		$scope.toggle();
	});

	$scope.$on('toggleProfileOpen', function() {
		$scope.activeAlert = alertService.activeAlert;
		$scope.updateProfile(function(profile) {
			$scope.isProfileVisible = true;
			$rootScope.profileIsOpen = true;
			$rootScope.$broadcast('profileWasOpened');
			$rootScope.$broadcast('profileWasUpdated');
			setTimeout($scope.updateProfile, 10000);
		});
	});

	$scope.updateProfile = function(callback) {
		alertService.getUserProfileForActiveAlert(function(profile) {
			$scope.currentProfile = profile;
			if (callback) {
				callback(profile);
			}
		});
	}

	$scope.shouldDisplayProfileButtons = function() {
		if ($scope.activeAlert && $scope.activeAlert.status == 'A') {
			return true;
		}
		return false;
	}

	$scope.markActiveAlertAsCompleted = function() {
		$scope.activeAlert.status = 'C';		
		$scope.toggle();
		clearActiveAlertMarker();
		$scope.returnToGeofenceCenter();
		$scope.dismissMarkCompletedModal();
		alertService.markActiveAlertAsCompleted(function(data) {
			$scope.activeAlert = null;
			alertService.activeAlert = null;
			$rootScope.$broadcast('alertMarkedChange');
			$rootScope.$broadcast('alertMarkedCompleted');
		});
	}

	$scope.markActiveAlertAsPending = function() {
		$scope.activeAlert.status = 'P';
		$scope.toggle();
		$scope.dismissMarkPendingModal();
		clearActiveAlertMarker();
		alertService.markActiveAlertAsPending(function(data) {
			$scope.activeAlert = null;
			alertService.activeAlert = null;
			$rootScope.$broadcast('alertMarkedChange');
			$rootScope.$broadcast('alertMarkedPending');
		});
	}

	$scope.getAge = function(dateString) {
	    var today = new Date();
	    var birthDate = new Date(dateString);
	    var age = today.getFullYear() - birthDate.getFullYear();
	    var m = today.getMonth() - birthDate.getMonth();
	    if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
	        age--;
	    }
	    return age;
	}

	$scope.getProfileImage = function() {
		if ($scope.currentProfile && $scope.currentProfile.profileImageURL) {
			return $scope.currentProfile.profileImageURL;
		}

		return '/media/static/shieldcommand/img/NoPicture_Image.png';
	}

	$scope.returnToGeofenceCenter = function () {
		setMapCenterToDefault();
	}

	$scope.zoomToActiveAlertMarker = function () {
		if ($scope.activeAlert) {
			setMarker($scope.activeAlert.location);
		};
	}

}])

.controller('AlertsListController', ['$rootScope', '$scope', '$filter', 'alertService', function($rootScope, $scope, $filter, alertService) {

	$scope.alerts = [];
	$rootScope.chats = {};
	$scope.myAlertsLength = 0;
	$scope.newAlertsLength = 0;
	$scope.pendingAlertsLength = 0;
	$scope.completedAlertsLength = 0;
	$scope.currentProfile = null;
	$scope.markerSetForActiveAlert = false;
	$scope.chatUpdateTimeout = null;
	$scope.newAlertSoundInterval = null;
	$scope.currentActiveLocation = null;

	$scope.$on('alertMarkedChange', function() {
		updateDisplay();
	});

	$scope.$on('profileWasUpdated', function() {
		updateDisplay();
	});

	$scope.$on('alertMarkedPending', function() {
		clearTimeout($scope.chatUpdateTimeout);
	});

	$scope.$on('alertMarkedCompleted', function() {
		clearTimeout($scope.chatUpdateTimeout);
	});

	$scope.$on('chatWindowOpened', function(event, alert) {
		if ((!alertService.activeAlert) || !(alert.object_id === alertService.activeAlert.object_id)) {
			$scope.alertClicked(alert);
		};
	});

	$scope.$watch('currentActiveLocation', function() {
		updateMarker($scope.currentActiveLocation);
		addressForLocation($scope.currentActiveLocation, function(address) {
			if (address) {
				alertService.activeAlert.geocodedAddress = address;
				$("#alert-address  p").html("<strong>Location:</strong> " + address);
				$("#alert-address").removeClass('hide');
			}
			else {
				$("#alert-address").addClass('hide');
			}
		});
		$scope.markerSetForActiveAlert = true;
	})

	$scope.$watch('newAlertsLength', function(newLength, oldLength) {
		if (newLength > oldLength) {
			if (alertService.activeAgency() && alertService.activeAgency().loopAlertSound) {
				newAlertSound.play();
				$scope.newAlertSoundInterval = setInterval(function () {
					newAlertSound.play();
				}, 2000);
			}
			else {
				newAlertSound.play();
			}
		}
		else if (newLength == 0) {
			newAlertSound.stop();
			clearInterval($scope.newAlertSoundInterval);
		}
	});

  	function updateAlerts(alerts) {
		$scope.alerts = alerts;
		$rootScope.alerts = $scope.alerts;
		updateDisplay();
  	};

  	function updateDisplay() {
		$scope.myAlertsLength = $filter("byAgencyDispatcher")($($filter("filter")($scope.alerts, {status: 'A'}))).length;
		$scope.newAlertsLength = $filter("filter")($scope.alerts, {status: 'N'}).length;
		$scope.pendingAlertsLength = $filter("filter")($scope.alerts, {status: 'P'}).length;
		$scope.completedAlertsLength = $filter("filter")($scope.alerts, {status: 'C'}).length;

		/* Don't call apply if we're already in the middle of a digest... */
		if ($scope.$root.$$phase != '$apply' && $scope.$root.$$phase != '$digest') {
			$scope.$apply();
		}
  	};

  	$scope.loadInitialAlerts = function() {
  		try {
			alertService.loadInitialAlerts(function(alerts) {
				updateAlerts(alerts);
				// setTimeout($scope.getUpdatedAlerts, 3000);
			});
		}
		catch (error) {
			console.log(error);
		}
		finally {
			setTimeout($scope.getUpdatedAlerts, 3000);
		}
  	};

  	$scope.getUpdatedAlerts = function() {
  		try {
	  		alertService.getUpdatedAlerts($scope.alerts, function(updatedAlerts) {
	  			updateAlerts(updatedAlerts);
				// setTimeout($scope.getUpdatedAlerts, 3000);
				if (alertService.activeAlert) {
					for (var i = 0; i < updatedAlerts.length; i++) {
						if (updatedAlerts[i].object_id == alertService.activeAlert.object_id) {
							$scope.currentActiveLocation = updatedAlerts[i].location;
						}
					}
				}
	  		});
		}
		catch (error) {
			console.log(error);
		}
		finally {
			setTimeout($scope.getUpdatedAlerts, 3000);
		}
  	}

  	$scope.alertClicked = function(alert) {
  		if (alert === alertService.activeAlert) {
  			$rootScope.$broadcast('toggleProfile');
  		}
  		else {
  			clearTimeout($scope.chatUpdateTimeout);
  			if (alertService.activeAlert) {
	  			$rootScope.$broadcast('closeChatWindowForAlert', alertService.activeAlert);
  			}
	  		alertService.setActiveAlert(alert);

  			$scope.initChatMessagesForActiveAlert();

	  		$scope.markerSetForActiveAlert = false;	

			if (alertService.activeAlert && !$scope.markerSetForActiveAlert) {
				setMarker(alertService.activeAlert.location);
				$scope.currentActiveLocation = alertService.activeAlert.location;
			}

  			$rootScope.$broadcast('activeAlertUpdated');
			$rootScope.$broadcast('toggleProfileOpen');
  		}
  	};

  	$scope.initChatMessagesForActiveAlert = function() {
  		try {
	  		if (alertService.activeAlert.object_id in $rootScope.chats) {
				alertService.activeAlert.chatMessages = $rootScope.chats[alertService.activeAlert.object_id].messages;
	  		}
	  		else {		
				alertService.getAllChatMessagesForActiveAlert(function(messages, latestTimestamp) {
					if (!(alertService.activeAlert.object_id in $rootScope.chats)) {
						$rootScope.chats[alertService.activeAlert.object_id] = {lastChecked: latestTimestamp, messages: []}
					}
					$rootScope.chats[alertService.activeAlert.object_id].messages = messages;
					$rootScope.chats[alertService.activeAlert.object_id].lastChecked = latestTimestamp;
					if (messages && messages.length > 0) {
						alertService.activeAlert.chatMessages = $rootScope.chats[alertService.activeAlert.object_id].messages;
						updateDisplay();
						newChatSound.play();
					}
				});
	  		}

			// if (alertService.activeAlert.status == 'A') {
			// 	$scope.chatUpdateTimeout = setTimeout($scope.updateChatMessages, 3000);
			// }
		}
		catch (error) {
			console.log(error);
		}
		finally {
			if (alertService.activeAlert.status == 'A') {
				$scope.chatUpdateTimeout = setTimeout($scope.updateChatMessages, 3000);
			}
		};
  	}

  	$scope.updateChatMessages = function () {
  		try {
	  		alertService.getNewChatMessagesForActiveAlert($rootScope.chats[alertService.activeAlert.object_id].lastChecked, function(messages, latestTimestamp) {
				if (messages && messages.length > 0) {
					var messageAdded = false;
					if (alertService.activeAlert && alertService.activeAlert.object_id in $rootScope.chats) {
						for (var i = 0; i < messages.length; i++) {
							var matchFound = false;
							for (var j = 0; j < $rootScope.chats[alertService.activeAlert.object_id].messages.length; j++) {
								if (messages[i].messageID == $rootScope.chats[alertService.activeAlert.object_id].messages[j].messageID) {
									matchFound = true;
								}
							}
							if (!matchFound) {
								$rootScope.chats[alertService.activeAlert.object_id].messages.push(messages[i]);
								messageAdded = true;
							}
						}
					}
					else {
						$rootScope.chats[alertService.activeAlert.object_id].messages = messages;
						messageAdded = true;
					}
					$rootScope.chats[alertService.activeAlert.object_id].lastChecked = latestTimestamp;
					alertService.activeAlert.chatMessages = $rootScope.chats[alertService.activeAlert.object_id].messages;
					updateDisplay();
					if (messageAdded) {
		  				newChatSound.play();
		  				$rootScope.$broadcast('newChatMessageReceived', alertService.activeAlert);
					}
				}
				// $scope.chatUpdateTimeout = setTimeout($scope.updateChatMessages, 3000);
			});
		}
		catch (error) {
			console.log(error);
		}
		finally {
			$scope.chatUpdateTimeout = setTimeout($scope.updateChatMessages, 3000);
		}
  	}

    $scope.selectedClass = function(alert) {
        return alert === alertService.activeAlert ? 'selected' : undefined;
    };

  	$scope.acceptClicked = function(alert) {
  		alert.status = 'A';
  		for (var i = 0; i < $scope.alerts.length; i++) {
  			if ($scope.alerts[i].object_id == alert.object_id) {
  				$scope.alerts[i].status = 'A';
  				$scope.alerts[i].agencyDispatcher = Javelin.activeAgencyUser.url;
  			}
  		};
  		updateDisplay();
		alertService.claimAlertForActiveUser(alert, function(data) {
			// Anything to do here?
		});

		if (alertService.activeAlert && (alert.object_id == alertService.activeAlert.object_id)) {
			$scope.initChatMessagesForActiveAlert();
		};
  	};

  	$scope.loadInitialAlerts();
}]);
