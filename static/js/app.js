'use strict';

var bikeApp = angular.module('bikeApp', [
    'facebook', 'ngRoute'
 ]);

bikeApp.config(['$routeProvider','FacebookProvider',
     function($routeProvider,FacebookProvider) {
         $routeProvider.
             when('/', {
                 templateUrl: '/static/pages/welcome.html'
             }).
             otherwise({
                 redirectTo: '/'
             });
         FacebookProvider.init('405452559812718')
    }]);

bikeApp.controller('loginController',[
    '$scope','Facebook', function ($scope,Facebook) {
        $scope.login = function () {
            Facebook.login(function (response) {
                console.log(response);
            });
        }
    }
]);
