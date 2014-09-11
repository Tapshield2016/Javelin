'use strict';

/* Filters */

angular.module('shieldCommand.filters', [])

.filter('interpolate', ['version', function(version) {
    return function(text) {
      return String(text).replace(/\%VERSION\%/mg, version);
    }
  }])

.filter('byAgencyDispatcher', [function() {
	return function(alerts) {
		var filtered = [];
		for (var i = 0; i < alerts.length; i++) {
			if (alerts[i].agencyDispatcher && alerts[i].agencyDispatcher.indexOf(Javelin.activeAgencyUser.url) !== -1) {
				filtered.push(alerts[i]);
			}
		};
		return filtered;
	}
}])

.filter('notActiveCrimeTip', [function() {
	return function(crimeTips, activeCrimeTip) {
		var filtered = [];
		for (var i = 0; i < crimeTips.length; i++) {
			if (activeCrimeTip && crimeTips[i].object_id != activeCrimeTip.object_id) {
				filtered.push(crimeTips[i]);
			}
		};
		return filtered;
	}
}])

.filter('locationsByStatusAndAgencyDispatcher', [function() {
	return function(alerts, statuses) {
		var filtered = [];
		for (var i = 0; i < alerts.length; i++) {
			if (statuses.indexOf(alerts[i].status) > -1) {
				var alert_type = alerts[i].initiatedBy;
                var title;
                if (alerts[i].agencyUser) {
                    title = alerts[i].agencyUserMeta.getFullName();
                }
                else {
                    title = alerts[i].staticDeviceMeta.description;
                }
				var location_info = { alertType: alerts[i].initiatedBy,
									  alertID: alerts[i].object_id,
									  title: title,
									  location: null }
				if (alerts[i].status == 'A') {
					if (alerts[i].agencyDispatcher && alerts[i].agencyDispatcher.indexOf(Javelin.activeAgencyUser.url) !== -1) {
						location_info.location = alerts[i].location;
						filtered.push(location_info);
					}
				}
				else {
					location_info.location = alerts[i].location;
					filtered.push(location_info);
				}
			}
		};
		return filtered;
	}
}]);
