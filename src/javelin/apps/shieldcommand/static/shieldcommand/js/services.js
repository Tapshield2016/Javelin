'use strict';

/* Services */


// Demonstrate how to register services
// In this case it is a simple value service.
angular.module('shieldCommand.services', []).
  value('version', '1.0');
