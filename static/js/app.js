'use strict';

var bikeApp = angular.module('bikeApp', [
    'ngRoute'
 ]);

bikeApp.run(function($rootScope, facebook) {
    $rootScope.Facebook = facebook;
});


bikeApp.factory('facebook', ['$window', function($window) {

    //get FB from the global (window) variable.
    var FB = $window.FB;

    // gripe if it's not there.
    if(!FB) throw new Error('Facebook not loaded');

    //make sure FB is initialized.
    FB.init({
        appId : '405452559812718',
        xfbml: true,
        version: 'v3.0'
    });

    return {
        // a me function
        login : function(callback) {
            FB.login(callback,{scope:'email,public_profile'});
        },
        
        logout: function (callback) {
            FB.logout(callback);
        }

    }
}]);

bikeApp.config(['$routeProvider',
     function($routeProvider) {
         $routeProvider.
             when('/', {
                 templateUrl: '/static/pages/welcome.html'
             }).
             otherwise({
                 redirectTo: '/'
             });
    }]);

bikeApp.controller('loginController',[
    '$scope','facebook', function ($scope,facebook) {
        $scope.login = function () {
            facebook.login(function (data) {
                console.log(data);
            });
        };
        $scope.logout = function () {
            facebook.login(function (data) {
                console.log(data);
            });
        }
    }
]);
