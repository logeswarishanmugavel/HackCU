'use strict';

angular.module('bikeApp', [
 'ngRoute'
 ]).
config(['$routeProvider',
     function($routeProvider) {
         $routeProvider.
             when('/', {
                 templateUrl: '/static/pages/welcome.html',
             }).
             otherwise({
                 redirectTo: '/'
             });
    }]);