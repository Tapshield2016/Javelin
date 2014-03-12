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
		if ($scope.activeAlert && $scope.activeAlert.status == 'A') { // need to check for agency dispatcher == active agency user
			if ($scope.activeAlert.agencyDispatcher.indexOf(Javelin.activeAgencyUser.url) > -1) {
				return true;
			}
		}
		return false;
	}

	$scope.shouldDisplayCompletedBy = function() {
		if ($scope.activeAlert && $scope.activeAlert.status == 'C') {
			return true;
		}
		return false;
	}

	$scope.markActiveAlertAsCompleted = function() {
		$scope.activeAlert.status = 'C';		
		$scope.toggle();
		clearActiveAlertMarker();
		$scope.returnToGeofenceCenter();
		$('#markAlertComplete').modal('hide');
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
		if (!dateString) {
			return '';
		}
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
			$scope.activeAlert.location.alertStatus = $scope.activeAlert.status;
			$scope.activeAlert.location.alertType = $scope.activeAlert.initiatedBy;
			$scope.activeAlert.location.title = $scope.activeAlert.agencyUserMeta.getFullName();
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
	$scope.chatUpdateInProgress = false;
	$scope.newAlertSoundInterval = null;
	$scope.newAlertDocumentTitleInterval = null;
	$scope.currentActiveLocation = null;

	$scope.$on('alertMarkedChange', function() {
		updateDisplay();
	});

	$scope.$on('profileWasUpdated', function() {
		updateDisplay();
	});

	$scope.$on('chatWasSent', function() {
		updateDisplay();
	});

	$scope.$on('alertMarkedPending', function() {
		clearTimeout($scope.chatUpdateTimeout);
		$scope.clearAddressBar();
	});

	$scope.$on('alertMarkedCompleted', function() {
		clearTimeout($scope.chatUpdateTimeout);
		$scope.clearAddressBar();
	});

	$scope.clearAddressBar = function() {
		$("#alert-address").addClass('hide');
		$("#alert-address  p").html("");
	}

	$scope.$on('chatWindowOpened', function(event, alert) {
		if ((!alertService.activeAlert) || !(alert.object_id === alertService.activeAlert.object_id)) {
			$scope.alertClicked(alert);
		};
	});

	$scope.$watch('currentActiveLocation', function() {
		updateMarker($scope.currentActiveLocation);
		addressForLocation($scope.currentActiveLocation, function(address) {
			if (!alertService.activeAlert) {
				return;
			}
			if (address) {
				alertService.activeAlert.geocodedAddress = address;
				$("#alert-address  p").html("<strong>Location:</strong> " + address);
				$("#alert-address").removeClass('hide');
			}
			else {
				$scope.clearAddressBar();
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

		if ($scope.myAlertsLength == 0 && $scope.newAlertsLength > 0) {
			if ($('#collapseTwo.in').length == 0) {
				$('.panel-new-alerts').click();
			}
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

		if ($scope.myAlertsLength == 0 && $scope.newAlertsLength > 0) {
			if ($('#collapseTwo.in').length == 0) {
				$('.panel-new-alerts').click();
			}
		}

		if ($scope.newAlertsLength > 0 || $scope.pendingAlertsLength > 0) {
				if (!$scope.newAlertDocumentTitleInterval) {
					$scope.newAlertDocumentTitleInterval = setInterval(function () {
						$scope.setDocumentTitle();
					}, 2000);
				}
		}
		else {
			if ($scope.newAlertDocumentTitleInterval) {
				clearInterval($scope.newAlertDocumentTitleInterval);
				$scope.newAlertDocumentTitleInterval = null;
			}
			document.title = "Shield Command";
		}
  	};

  	$scope.setDocumentTitle = function() {
  		if ($scope.newAlertsLength > 0 || $scope.pendingAlertsLength > 0) {
  			if (document.title === "Shield Command") {
  				document.title = "(" + ($scope.newAlertsLength + $scope.pendingAlertsLength) + ") - Shield Command";
  			}
  			else {
  				document.title = "Shield Command";
  			}
  		}
  	}

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
				if (alertService.activeAlert) {
					for (var i = 0; i < updatedAlerts.length; i++) {
						if (updatedAlerts[i].object_id == alertService.activeAlert.object_id) {
							if (updatedAlerts[i].location) {
								updatedAlerts[i].location.alertStatus = updatedAlerts[i].status;
								updatedAlerts[i].location.alertType = updatedAlerts[i].initiatedBy;
								updatedAlerts[i].location.title = updatedAlerts[i].agencyUserMeta.getFullName();
								$scope.currentActiveLocation = updatedAlerts[i].location;
								updateDisplay();
							}
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

    $scope.$on('alertPinClicked', function(event, alertID) {
		for (var i = 0; i < $scope.alerts.length; i++) {
			if ($scope.alerts[i].object_id == alertID) {
				$scope.alertClicked($scope.alerts[i]);

				var container = null;
				var currentlyOpen = $('.panel-collapse.in');
				if ($scope.alerts[i].status == 'A') {
					container = $("#collapseOne");
				}
				else if ($scope.alerts[i].status == 'N') {
					container = $("#collapseTwo");
				}
				else if ($scope.alerts[i].status == 'P') {
					container = $("#collapseThree");
				}
				else { // status == 'C'
					container = $("#collapseFour");
				}

				if (!(container[0] == currentlyOpen[0])) {
					container.prevAll('.panel-heading').click();
				}

				var scrollTo = $("#" + alertID);
				var scrollContainer = container.find('.panel-body');
				scrollContainer.animate({
				    scrollTop: scrollTo.offset().top - scrollContainer.offset().top + scrollContainer.scrollTop()
				});
			}
		};    	
    });

  	$scope.alertClicked = function(alert, shouldToggleProfile) {
  		shouldToggleProfile = typeof shouldToggleProfile !== 'undefined' ? shouldToggleProfile : true;
  		if (alert === alertService.activeAlert) {
  			if (shouldToggleProfile) {
	  			$rootScope.$broadcast('toggleProfile');
  			}
  			$scope.initChatMessagesForActiveAlert();
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
				if (alertService.activeAlert.location) {
					alertService.activeAlert.location.alertStatus = alertService.activeAlert.status;
					alertService.activeAlert.location.alertType = alertService.activeAlert.initiatedBy;
					alertService.activeAlert.location.title = alertService.activeAlert.agencyUserMeta.getFullName();
					setMarker(alertService.activeAlert.location);
					$scope.currentActiveLocation = alertService.activeAlert.location;
				}
			}

  			$rootScope.$broadcast('activeAlertUpdated');
			$rootScope.$broadcast('toggleProfileOpen');
  		}
  	};

  	$scope.initChatMessagesForActiveAlert = function() {
		$scope.chatUpdateInProgress = false;
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
						$rootScope.$broadcast('newChatMessageReceived', alertService.activeAlert);
						updateDisplay();
						newChatSound.play();
					}
				});
	  		}
		}
		catch (error) {
			console.log(error);
			$scope.chatUpdateInProgress = false;
		}
		finally {
			if (alertService.activeAlert.status == 'A') {
				$scope.chatUpdateTimeout = setTimeout($scope.updateChatMessages, 3000);
			}
		};
  	}

  	$scope.updateChatMessages = function () {
  		try {
  			if (!$scope.chatUpdateInProgress) {
  				$scope.chatUpdateInProgress = true;
	  			var alertID = alertService.activeAlert.object_id
		  		alertService.getNewChatMessagesForActiveAlert($rootScope.chats[alertID].lastChecked, function(messages, latestTimestamp) {
					if (messages && messages.length > 0) {
						var messageAdded = false;
						if (alertID in $rootScope.chats) {
							for (var i = 0; i < messages.length; i++) {
								var matchFound = false;
								for (var j = 0; j < $rootScope.chats[alertID].messages.length; j++) {
									if (messages[i].messageID == $rootScope.chats[alertID].messages[j].messageID) {
										matchFound = true;
									}
								}
								if (!matchFound) {
									$rootScope.chats[alertID].messages.push(messages[i]);
									messageAdded = true;
								}
							}
						}
						else {
							$rootScope.chats[alertID].messages = messages;
							messageAdded = true;
						}
						$rootScope.chats[alertID].lastChecked = latestTimestamp;
						alertService.activeAlert.chatMessages = $rootScope.chats[alertID].messages;
						updateDisplay();
						if (messageAdded) {
			  				newChatSound.play();
			  				$rootScope.$broadcast('newChatMessageReceived', alertService.activeAlert);
						}
					}
					$scope.chatUpdateInProgress = false;
				});
  			}
  			else {
  				console.log("Chat update in progress!");
  			}

		}
		catch (error) {
			console.log(error);
			$scope.chatUpdateInProgress = false;
		}
		finally {
			$scope.chatUpdateTimeout = setTimeout($scope.updateChatMessages, 3000);
		}
  	}

    $scope.selectedClass = function(alert) {
        return alert === alertService.activeAlert ? 'selected' : undefined;
    };

  	$scope.acceptClicked = function(alert) {
  		var acceptedFromNew = (alert.status == 'N');
  		var acceptedFromPending = (alert.status == 'P');
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

		if (alert === alertService.activeAlert) {
			$scope.alertClicked(alert, false);
		}
		else {
			$scope.alertClicked(alert);
		}
		$('.accordion-default').click();
		setTimeout(function() {
			$('#chat-icon-' + alert.object_id).click();
		}, 1000);
  	};

  	$scope.loadInitialAlerts();
}]);
