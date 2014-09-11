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

.controller('UserProfileController', ['$rootScope', '$scope', 'alertService', 'crimeTipService', function($rootScope, $scope, alertService, crimeTipService) {

	$scope.currentProfile = null;
	$scope.activeAlert = null;
	$scope.activeCrimeTip = null;
	$scope.profileType = null;
	$scope.isProfileVisible = false;
    $scope.isAcceptingAlert = false;
	$scope.updateTimeout = null;
	$rootScope.profileIsOpen = false;
	$scope.spotCrimes = [];
	$scope.spotCrimeUpdateInterval = 60;

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

    $scope.close = function() {
		if ($scope.isProfileVisible) {
            $scope.isProfileVisible = !$scope.isProfileVisible;
			$rootScope.$broadcast('profileWasClosed');
			$rootScope.profileIsOpen = false;
		}
	}

	$scope.$on('toggleProfile', function() {
		$scope.toggle();
	});

	$scope.$on('toggleProfileOpen', function() {
		if ($scope.updateTimeout)
		{
			clearTimeout($scope.updateTimeout);
		}
		
		if (alertService.activeAlert)
		{
            if (alertService.activeAlert.staticDevice) {
                $scope.profileType = 'staticAlert';
            }
            else {
                $scope.profileType = 'alert';
            }
			$scope.activeAlert = alertService.activeAlert;
			$scope.activeCrimeTip = null;
		}
		else if (crimeTipService.activeCrimeTip)
		{
			$scope.profileType = 'crimeTip';
			$scope.activeCrimeTip = crimeTipService.activeCrimeTip;
			$scope.activeAlert = null;
		}
		if ($scope.activeAlert || $scope.activeCrimeTip)
		{
			$scope.isProfileVisible = true;
			$rootScope.profileIsOpen = true;
			$rootScope.$broadcast('profileWasOpened');
			$scope.updateProfile(function(profile) {
				$rootScope.$broadcast('profileWasUpdated');
				$scope.updateTimeout = setTimeout($scope.updateProfile, 10000);
            });
		}
	});

	$scope.updateProfile = function(callback) {
		if ($scope.activeAlert)
		{
            if ($scope.activeAlert.staticDevice) {
                $scope.currentProfile = $scope.activeAlert.staticDeviceMeta;
            }
            else {
                alertService.getUserProfileForActiveAlert(function(profile) {
                    $scope.currentProfile = profile;
                    if (callback) {
					    callback(profile);
				    }
			    });
            }
		}
		else if ($scope.activeCrimeTip)
		{
			if (! $scope.activeCrimeTip.anonymous)
			{
				crimeTipService.getUserForActiveCrimeTip(function(user)
				{ 
					$scope.currentProfile = user;
					if (callback) {
						callback(user);
					}
				});
			}
			else
			{
				$scope.currentProfile = null;
			}
			
			if ($scope.activeCrimeTip.viewedBy)
			{
                if ($scope.activeCrimeTip.dispatcherName) {
                    $scope.activeCrimeTip.viewedByName = $scope.activeCrimeTip.dispatcherName;
                }
                else {
				    crimeTipService.getUserForCrimeTipViewed(function(user) {
				    	$scope.activeCrimeTip.viewedByName = user.getFullName();
				    });
                }
			}
			else if ($scope.activeCrimeTip.flaggedBy)
			{
                if ($scope.activeCrimeTip.dispatcherName) {
                    $scope.activeCrimeTip.flaggedByName = $scope.activeCrimeTip.dispatcherName;
                }
                else {
                    crimeTipService.getUserForCrimeTipFlagged(function (user) {
                        $scope.activeCrimeTip.flaggedByName = user.getFullName();
                    });
                }
			}
		}
		else
		{
			$scope.currentProfile = null;
			
			if (callback)
			{
				callback(null);
			}
		}
	}

	$scope.shouldDisplayProfileButtons = function() {
		if ($scope.activeAlert && $scope.activeAlert.status == 'A') { // need to check for agency dispatcher == active agency user
			if ($scope.activeAlert.agencyDispatcher.indexOf(Javelin.activeAgencyUser.url) > -1) {
				return true;
			}
		}
		return false;
	}
	
	$scope.shouldDisplayCrimeTipButtons = function() {
		if ($scope.activeCrimeTip && $scope.activeCrimeTip.flaggedSpam == false && $scope.activeCrimeTip.viewedTime == null) {
			return true;
		}
		return false;
	}

	$scope.shouldDisplayCompletedBy = function() {
		if ($scope.activeAlert && $scope.activeAlert.status == 'C') {
			return true;
		}
		return false;
	}
	
	$scope.shouldDisplayViewedBy = function() {
		if ($scope.activeCrimeTip && $scope.activeCrimeTip.viewedBy) {
			return true;
		}
		return false;
	}
	
	$scope.shouldDisplayFlaggedBy = function() {
		if ($scope.activeCrimeTip && $scope.activeCrimeTip.flaggedBy) {
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
	
	$scope.markCrimeTipViewed = function() {
		$scope.toggle();
		var crimeTips = [];
		crimeTips.push($scope.activeCrimeTip);
		hideCrimeMarkers(crimeTips);
		clearActiveAlertMarker();
		$scope.returnToGeofenceCenter();
		var $crimeTip = $('#crimeTip-' + $scope.activeCrimeTip.object_id);
		$crimeTip.find('.badge-viewed').removeClass('hidden');
		$crimeTip.fadeTo('fast', 0.5);
		crimeTipService.markCrimeTipViewed(function(data) {
			$scope.activeCrimeTip = null;
			crimeTipService.activeCrimeTip = null;
			$rootScope.$broadcast('crimeTipMarkedChange');
		});
	}
	
	$scope.markCrimeTipSpam = function() {
		$scope.toggle();
		var crimeTips = [];
		crimeTips.push($scope.activeCrimeTip);
		hideCrimeMarkers(crimeTips);
		clearActiveAlertMarker();
		$scope.returnToGeofenceCenter();
		var $crimeTip = $('#crimeTip-' + $scope.activeCrimeTip.object_id);
		$crimeTip.find('.badge-spam').removeClass('hidden');
		$crimeTip.fadeTo('fast', 0.2);
		crimeTipService.markCrimeTipSpam(function(data) {
			$scope.activeCrimeTip = null;
			crimeTipService.activeCrimeTip = null;
			$rootScope.$broadcast('crimeTipMarkedChange');
		});
	}

    $scope.$on('acceptingAlert', function () {
        $scope.isAcceptingAlert = true;
	});

    $scope.$on('resetAll', function () {

        if ($scope.isAcceptingAlert) {
            $scope.isAcceptingAlert = false;
            return;
        }

        $scope.close();
		var crimeTips = [];
		crimeTips.push($scope.activeCrimeTip);
		hideCrimeMarkers(crimeTips);
		clearActiveAlertMarker();
		$scope.returnToGeofenceCenter();
        $scope.activeAlert = null;
        alertService.activeAlert = null;
	});


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
		closeInfoWindow();
	}

	$scope.zoomToActiveAlertMarker = function () {
		if ($scope.profileType == 'alert' && $scope.activeAlert) {
			$scope.activeAlert.location.alertStatus = $scope.activeAlert.status;
			$scope.activeAlert.location.alertType = $scope.activeAlert.initiatedBy;
            alertService.activeAlert.location.title = alertService.activeAlert.agencyUserMeta.getFullName();
			setMarker($scope.activeAlert.location);
			closeInfoWindow();
		}
        else if ($scope.profileType == 'staticAlert' && $scope.activeAlert) {
            $scope.activeAlert.location.alertStatus = $scope.activeAlert.status;
			$scope.activeAlert.location.alertType = $scope.activeAlert.initiatedBy;
            alertService.activeAlert.location.title = alertService.activeAlert.staticDeviceMeta.description;
			setMarker($scope.activeAlert.location);
			closeInfoWindow();
        }
		else if ($scope.profileType == 'crimeTip' && $scope.activeCrimeTip)
		{
			showCrimeMarker($scope.activeCrimeTip);
			zoomToCrime($scope.activeCrimeTip);
		}
	}
	
	$scope.getFileType = function(filename) {
		return filename.split('.').pop().toLowerCase();
	}
	
	$scope.isAudioSupported = function(filename) {
		if ( ! buzz.isSupported())
		{
			console.log('buzz not supported');
			return false;
		}
		
		var format = $scope.getFileType(filename);
		
		switch(format)
		{
			case 'ogg':
				console.log('ogg: ' + buzz.isOGGSupported());
				return buzz.isOGGSupported();
			case 'wav':
				console.log('wav: ' + buzz.isOGGSupported());
				return buzz.isWAVSupported();
			case 'mp3':
				console.log('mp3: ' + buzz.isOGGSupported());
				return buzz.isMP3Supported();
			case 'aac':
			case 'mp4':
			case 'm4a':
			case '3gp':
				console.log('aac: ' + buzz.isOGGSupported());
				return buzz.isAACSupported();
			default:
				return false;
		}
	}
	
	$scope.isVideoSupported = function(filename) {
		if ( ! Modernizr.video)
		{
			console.log('video not supported');
			return false;
		}
		
		var format = $scope.getFileType(filename);
		
		switch(format)
		{
			case 'ogg':
				console.log('ogg video: ' + Modernizr.video.ogg);
				return Modernizr.video.ogg;
			case 'mp4':
				console.log('mp4 video: ' + Modernizr.video.h264);
				return Modernizr.video.h264;
			default:
				return false;
		}
	}
	
	$scope.playAudio = function(filename) {
		if ( ! $scope.isAudioSupported(filename))
		{
			return false;
		}
		
		var audio = new buzz.sound(filename);
		console.log('playing audio');
		audio.play();
	}
	
	$scope.getSpotCrimes = function() {
		Javelin.getSpotCrimes(function(spotCrimes) {
			hideCrimeMarkers($($scope.spotCrimes).not(spotCrimes).get());
			var newSpotCrimes = $(spotCrimes).not($scope.spotCrimes).get();
			addCrimeMarkers(newSpotCrimes);
			showCrimeMarkers(newSpotCrimes);
			$scope.spotCrimes = spotCrimes;
		});
		
		setTimeout($scope.getSpotCrimes, $scope.spotCrimeUpdateInterval * 1000);
	}
	
	setTimeout($scope.getSpotCrimes, 2500);

}])

.controller('AlertsListController', ['$rootScope', '$scope', '$filter', 'alertService', 'crimeTipService', function($rootScope, $scope, $filter, alertService, crimeTipService) {

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
    $scope.newCrimeTipSoundInterval = null;
	$scope.newAlertDocumentTitleInterval = null;
	$scope.currentActiveLocation = null;
	$scope.crimeTips = [];
	$scope.crimeTipsLength = 0;
    $scope.unviewedCrimeTipsLength = 0;
	$scope.crimeTipUpdateInterval = 20;
	$scope.markerSetForActiveCrimeTip = false;

	$scope.$on('alertMarkedChange', function() {
		updateDisplay();
	});

    $rootScope.$on('crimeTipMarkedChange', function() {
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
		if ($scope.currentActiveLocation)
		{
			if ($scope.currentActiveLocation.type == 'alert')
			{
                var crimeTips = [];
		        crimeTips.push(crimeTipService.activeCrimeTip);
		        hideCrimeMarkers(crimeTips);
				updateMarker($scope.currentActiveLocation);
				crimeTipService.activeCrimeTip = null;
				$scope.markerSetForActiveAlert = true;
				$scope.markerSetForActiveCrimeTip = false;
			}
			else if ($scope.currentActiveLocation.type == 'crimeTip')
			{
				zoomToCrime($scope.currentActiveLocation);
				alertService.activeAlert = null;
				$scope.markerSetForActiveCrimeTip = true;
				$scope.markerSetForActiveAlert = false;
			}
		}
		addressForLocation($scope.currentActiveLocation, function(address) {
			if (address)
			{
				if ($scope.currentActiveLocation.type == 'alert' && alertService.activeAlert)
				{
					alertService.activeAlert.geocodedAddress = address;
				}
				else if ($scope.currentActiveLocation.type == 'crimeTip' && crimeTipService.activeCrimeTip)
				{
					crimeTipService.activeCrimeTip.geocodedAddress = address;
				}
				else
				{
					address = null;
				}
				
			}
			
			if (address)
			{
				$("#alert-address  p").html("<strong>Approx Location:</strong> " + address);
				$("#alert-address").removeClass('hide');
			}
			else
			{
				$scope.clearAddressBar();
			}
		});
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
	
	$scope.$watch('unviewedCrimeTipsLength', function(newLength, oldLength) {

		if (newLength > 0) {
            if (alertService.activeAgency() && alertService.activeAgency().loopAlertSound) {
                newCrimeTipSound.play();
                $scope.flashPanel($('#crimeTipListLink'));
                $scope.newCrimeTipSoundInterval = setInterval(function () {
					newCrimeTipSound.play();
                    $scope.flashPanel($('#crimeTipListLink'));
				}, 2000);
            }
            else {
                newCrimeTipSound.play();
                $scope.flashPanel($('#crimeTipListLink'));
            }
		}
        else if (newLength == 0) {
			newCrimeTipSound.stop();
			clearInterval($scope.newCrimeTipSoundInterval);
		}
	});

    $scope.flashPanel = function ($panel) {
		var bgColor = $panel.css('background-color');
		var flashes = 0;

		var i = setInterval(function() {
			if ($panel.css('background-color') == bgColor)
			{
				$panel.css('background-color', '#3AA1D3');
			}
			else
			{
				$panel.css('background-color', bgColor);
			}

			flashes++;

			if (flashes == 8)
			{
				clearInterval(i);
			}
		}, 300);
    }
	
	$scope.$watch('crimeTipsVisible', function(visible, oldValue) {
		if (visible == false && oldValue == true)
		{
			$rootScope.$broadcast('toggleProfile');
		}
	});

  	function updateAlerts(alerts) {
		$scope.alerts = alerts;
		$rootScope.alerts = $scope.alerts;
		updateDisplay();
  	};
	
	function updateCrimeTips(crimeTips) {
		$scope.crimeTips = crimeTips;
		$rootScope.crimeTips = crimeTips;
		updateDisplay();
  	};

  	function updateDisplay() {
		$scope.myAlertsLength = $filter("byAgencyDispatcher")($($filter("filter")($scope.alerts, {status: 'A'}))).length;
		$scope.newAlertsLength = $filter("filter")($scope.alerts, {status: 'N'}).length;
		$scope.pendingAlertsLength = $filter("filter")($scope.alerts, {status: 'P'}).length;
		$scope.completedAlertsLength = $filter("filter")($scope.alerts, {status: 'C'}).length;

        if ($scope.crimeTips) {
            $scope.crimeTipsLength = $scope.crimeTips.length;
            var count = 0;
            for (var i=0; i<$scope.crimeTips.length; i++) {
                if (!$scope.crimeTips[i].viewedBy && !$scope.crimeTips[i].flaggedSpam) {
                    count++;
                }
            }
            $scope.unviewedCrimeTipsLength = count;
        }

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
		
		if ($scope.crimeTipsLength > 0)
		{
			addCrimeMarkers($scope.crimeTips);
			var crimeMarkersForRemoval = $filter("filter")($scope.crimeTips, {showPin: false});
			hideCrimeMarkers($filter("notActiveCrimeTip")(crimeMarkersForRemoval, crimeTipService.activeCrimeTip));
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
	
	$scope.loadInitialCrimeTips = function() {
  		try {
			crimeTipService.loadInitialCrimeTips(function(crimeTips) {
				updateCrimeTips(crimeTips);
			});
		}
		catch (error) {
			console.log(error);
		}
		finally {
			setTimeout($scope.getUpdatedCrimeTips, $scope.crimeTipUpdateInterval * 1000);
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
                                if (updatedAlerts[i].agencyUser) {
                                    updatedAlerts[i].location.title = updatedAlerts[i].agencyUserMeta.getFullName();
                                }
                                else {
                                    updatedAlerts[i].location.title = updatedAlerts[i].staticDeviceMeta.description;
                                }
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
	
	$scope.getUpdatedCrimeTips = function() {
  		try {
	  		crimeTipService.getUpdatedCrimeTips($scope.crimeTips, function(updatedCrimeTips) {
	  			updateCrimeTips(updatedCrimeTips);
				if (crimeTipService.activeCrimeTip) {
					for (var i = 0; i < updatedCrimeTips.length; i++) {
						if (updatedCrimeTips[i].object_id == crimeTipService.activeCrimeTip.object_id) {
							$scope.currentActiveLocation = updatedCrimeTips[i];
							updateDisplay();
						}
					}
				}
	  		});
		}
		catch (error) {
			console.log(error);
		}
		finally {
			setTimeout($scope.getUpdatedCrimeTips, $scope.crimeTipUpdateInterval * 1000);
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

        //Accordian button clicked
	$scope.panelClicked = function(panel) {

        $rootScope.$broadcast('resetAll');

//		if (panel != 'crimeTip')
//		{
//			if (crimeTipService.activeCrimeTip && $rootScope.profileIsOpen)
//			{
//				$rootScope.$broadcast('toggleProfile');
//			}
//		}
	}

//  Alert is clicked from list.  Needs to display marker, show profile, and load an chat messages.
  	$scope.alertClicked = function(alert, shouldToggleProfile) {
  		shouldToggleProfile = typeof shouldToggleProfile !== 'undefined' ? shouldToggleProfile : true;
  		if (alert === alertService.activeAlert) {
            //If alert clicked is already the active alert close the profile
  			if (shouldToggleProfile) {
	  			$rootScope.$broadcast('toggleProfile');
  			}
  			$scope.initChatMessagesForActiveAlert();
  		}
  		else {
  			clearTimeout($scope.chatUpdateTimeout);
  			if (alertService.activeAlert) {
                //  If active alert already exists close the chat window before loading a new alert
	  			$rootScope.$broadcast('closeChatWindowForAlert', alertService.activeAlert);
  			}
	  		alertService.setActiveAlert(alert);

  			$scope.initChatMessagesForActiveAlert();

	  		$scope.markerSetForActiveAlert = false;	

            //  Set the alert marker from location
			if (alertService.activeAlert && !$scope.markerSetForActiveAlert) {
				if (alertService.activeAlert.location) {
					alertService.activeAlert.location.alertStatus = alertService.activeAlert.status;
					alertService.activeAlert.location.alertType = alertService.activeAlert.initiatedBy;

                    if (alertService.activeAlert.agencyUser) {
                        alertService.activeAlert.location.title = alertService.activeAlert.agencyUserMeta.getFullName();
                    }
                    else {
                        alertService.activeAlert.location.title = alertService.activeAlert.staticDeviceMeta.description;
                    }

					setMarker(alertService.activeAlert.location);
					$scope.currentActiveLocation = alertService.activeAlert.location;
				}
			}

  			$rootScope.$broadcast('activeAlertUpdated');
			$rootScope.$broadcast('toggleProfileOpen');
  		}
  	};

//    Crime tip clicked from list. Toggle profile to show crime tip info. Dismiss any current active alerts
	$scope.crimeTipClicked = function(crimeTip, shouldToggleProfile) {
  		shouldToggleProfile = typeof shouldToggleProfile !== 'undefined' ? shouldToggleProfile : true;
  		if (crimeTip === crimeTipService.activeCrimeTip) {
  			if (shouldToggleProfile) {
	  			$rootScope.$broadcast('toggleProfile');
  			}
  		}
  		else {
	  		crimeTipService.setActiveCrimeTip(crimeTip);
			alertService.setActiveAlert(null);
	  		$scope.markerSetForActiveCrimeTip = false;	

			if (crimeTipService.activeCrimeTip && !$scope.markerSetForActiveCrimeTip) {
				if (crimeTipService.activeCrimeTip) {

					showCrimeMarker(crimeTipService.activeCrimeTip);
					
					$scope.currentActiveLocation = crimeTipService.activeCrimeTip;
				}
			}

  			$rootScope.$broadcast('activeCrimeTipUpdated');
			$rootScope.$broadcast('toggleProfileOpen');
  		}
  	};

  	$scope.initChatMessagesForActiveAlert = function() {
		$scope.chatUpdateInProgress = false;
        if (!alertService.activeAlert.agencyUser) {
            return;
        }
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
        if (!alertService.activeAlert) {
            $scope.chatUpdateInProgress = false;
            return;
        }
        if (!alertService.activeAlert.agencyUser) {
            $scope.chatUpdateInProgress = false;
            return;
        }
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
				$scope.chatUpdateInProgress = false;
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

    $scope.selectedClass = function(obj) {
        if (obj.type == 'alert')
		{
			return obj === alertService.activeAlert ? 'selected' : undefined;
		}
		else if (obj.type == 'crimeTip')
		{
			return obj === crimeTipService.activeCrimeTip ? 'selected' : undefined;
		}
		else
		{
			return undefined;
		}
    };

  	$scope.acceptClicked = function(alert) {
  		var acceptedFromNew = (alert.status == 'N');
  		var acceptedFromPending = (alert.status == 'P');
        $rootScope.$broadcast('acceptingAlert');
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
        setTimeout(function() {
            $('.accordion-default').click();
		});
		setTimeout(function() {
			$('#chat-icon-' + alert.object_id).click();
		}, 1000);
  	};

  	$scope.loadInitialAlerts();
	setTimeout($scope.loadInitialCrimeTips, 1500);
}]);
