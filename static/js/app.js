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
        version: 'v2.9'
    });

    return {
        // a me function
        login : function(callback) {
            FB.login(callback,{scope:'email,public_profile,user_friends'});
        },
        logout: function (callback) {
            FB.logout(callback);
        },
        friendslist: function (callback) {
            FB.api("/me",{fields: 'friends'},callback);
        },
        details: function (callback) {
            FB.api("/me",{fields: 'email,gender,name,age_range'},callback);
        },
        checkLogin: function(callback){
            FB.getLoginStatus(callback);
        }

    }
}]);

bikeApp.config(['$routeProvider','$locationProvider',
     function($routeProvider,$locationProvider) {
         $routeProvider.
             when('/', {
                 templateUrl: '/static/pages/welcome.html',
                 controller: 'loginController'
             }).
             when('/directions', {
                 templateUrl: '/static/pages/directions.html',
                 controller: 'loginController'
             }).
             when('/friends', {
                  templateUrl: '/static/pages/friends.html',
                  controller: 'loginController'
              }).
             otherwise({
                 redirectTo: '/'
             });

         $locationProvider.hashPrefix('');
    }]);

bikeApp.controller('loginController',[
    '$scope','$http','$route','facebook', function ($scope,$http,$route,facebook) {
        var user_id = '';
        var loginstatus = false;
        var fb_id = '';
        $scope.routeinfo = [];
        $scope.frndrouteinfo = [];
        $scope.result = [];
        $scope.friendsinfo = [];
        var getuserinfo = function(user_id){
            $http({
                      method: 'GET',
                      url: '/getuserinfo/'+user_id
               }).then(function(response) {
                    console.log(response.data);
                    $scope.routeinfo = response.data.result.route_list;
                    $scope.friendsinfo = response.data.result.friends_list;
                    getfriendsinfo();
               });
        }
        var getfriendsinfo = function(){
            console.log($scope.friendsinfo);
            for(var i=0;i<$scope.friendsinfo.length;i++){
                $http({
                      method: 'GET',
                      url: '/getuserinfo/'+$scope.friendsinfo[i].friend_id
               }).then(function(response) {
                    console.log(response.data.result);
                    $scope.result.push(response.data.result);
               });
             }
             console.log($scope.result);
        }
        $scope.onpageload = function(){
                 facebook.checkLogin(function (response){
                        console.log(response);
                        if(response.status ==='connected'){
                            loginstatus = true;
                            $scope.loginform = false;
                            $scope.mysavedroutes = true;
                            fb_id = response.authResponse.userID;
                            facebook.details(function (details){
                                $scope.loginform = false;
                                $http({
                                       method: 'GET',
                                       url: '/getuserid/'+fb_id
                                }).then(function(response) {
                                       user_id = response.data.user_id;
                                       getuserinfo(user_id);

                                }, function(error) {
                                       console.log(error);
                                });
                            });
                        }
                        else{
                            loginstatus = false;
                            $scope.loginform = true;
                            $scope.mysavedroutes = false;
                        }
                    });
        }
        $scope.getfrienddetails = function(){
            for(i=0;i<$scope.friendslist.length;i++){
                console.log("Hello");
            }
        }
        $scope.login = function () {
            if(!loginstatus){
            facebook.login(function (loginData) {
                facebook.details(function (details) {
                    var re_details = {};
                    re_details["name"] = details["name"];
                    re_details["age"] = parseInt(details["age_range"]["min"]);
                    re_details["gender"]  = details["gender"];
                    re_details["email_id"] = details["email"];
                    re_details["fb_id"] = details["id"];
                    var req = {
                        method: 'POST',
                        url: '/adduser',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        data: JSON.stringify(re_details)
                    };
                    console.log (req);
                    $http(req).then(function (resp) {
                        loginstatus = true;
                        $scope.loginform = false;
                        $scope.mysavedroutes = true;
                        $http({
                        	method: 'GET',
                        	url: '/getuserid/'+re_details["fb_id"]
                        }).then(function(response) {
                            user_id = response.data.user_id;
                            getuserinfo(user_id);
                        }, function(error) {
                          	console.log(error);
                        });
                    });
                });
            });

            }else{
                facebook.details(function (details){
                    $scope.loginform = false;
                    $http({
                           method: 'GET',
                           url: '/getuserid/'+fb_id
                    }).then(function(response) {
                           console.log(response);
                    }, function(error) {
                           console.log(error);
                    });
                });
            }
        }

        $scope.friendslist = function () {
            facebook.friendslist(function(response){
                console.log(response);
            });
        }
        $scope.logout = function () {
            facebook.logout(function (response) {
                console.log(response);
                $scope.loginform = true;
                $scope.mysavedroutes = false;
                loginstatus = false;
                $route.reload();
            });
        }
        /*
    }
]);

bikeApp.controller('RouteController',['$scope','$http','facebook', function ($scope,$http,facebook) {
*/

    $scope.narratives = [];
    var directionresponsedata = undefined;
    var loginstatus = false;
    var fb_id,user_id;
    $scope.savebutton = false;
    $scope.successmsg = false;
    var map;
    var plotmap = function(waypoints){
        if(map){
            map.remove();
        }
        map = L.map('map', {
            layers: MQ.mapLayer(),
            dragging: true
        });
        console.log(waypoints);
        var control = L.Routing.control({
             waypoints: waypoints,
             draggableWaypoints: false,
             show: false,
             createMarker: function(i,waypoints,n){
                if(i==0||i==n-1)
                    return L.marker(waypoints.latLng);
               }
        }).addTo(map);
    }
    $scope.showroutes = function(data){
        console.log(data);
        $scope.frndrouteinfo = data;
    }
    $scope.savedroutes = function(data){
        var pdata = JSON.parse(data);
        console.log(pdata);
        plotmap(pdata);
    }

    $scope.getdirections = function(){
            var src = $scope.route.source;
            var dest = $scope.route.destination;
            $http({
                method: 'GET',
                url: '/getDirections/'+src+"/"+dest
            }).then(function(response) {
                console.log(response);
                $scope.narratives = response.data.narratives;
                directionresponsedata = response.data.lat_long;
                $scope.savebutton = true;
                plotmap(directionresponsedata);
            }, function(error) {
                console.log(error);
            });

    }

    $scope.saveRoute = function(){
        var data = {};
        data["from_lat"] = directionresponsedata[0]["lat"];
        data["from_lng"] = directionresponsedata[0]["lng"];
        data["to_lat"] = directionresponsedata[length-1]["lat"];
        data["to_lng"] = directionresponsedata[length-1]["lng"];
        data["info"] = JSON.stringify(directionresponsedata);

        console.log(data);
        $http({
            method: 'POST',
            url: '/addrouteinfo',
            headers: {
                'Content-Type': 'application/json'
            },
            data: data
        }).then(function(response) {
                console.log(response);
                var userroutedata = {};
                var today = new Date();
                var dd = today.getDate();
                var mm = today.getMonth()+1;
                var yy = today.getFullYear().toString().substr(2,2);
                if(dd<10){
                    dd='0'+dd;
                }
                if(mm<10){
                    mm='0'+mm;
                }
                var today = mm+'/'+dd+'/'+yy;
                userroutedata["user_id"]=user_id;
                userroutedata["trip_date"] = today;
                userroutedata["route_id"] = response["data"]["route_id"];
                //userroutedata["route_info"] = '';

                     $http({
                           method: 'POST',
                           url: '/adduserrouteinfo',
                           headers: {
                               'Content-Type': 'application/json'
                           },
                           data: userroutedata
                       }).then(function(response) {
                            console.log(response);
                        }, function(error) {
                         console.log(error);
                     });

        }, function(error) {
                         console.log(error);
                     });
    }
}]);