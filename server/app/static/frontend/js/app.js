'use strict';

/* App Module */

var shareWalletApp = angular.module('shareWalletApp', [
  'ngRoute',
  'ShareWalletControllers',
  'LoginControllers',
  'APIServices',
]);

shareWalletApp.config(['$routeProvider', '$httpProvider',
  function($routeProvider, $httpProvider) {
    $routeProvider.
      when('/login', {
        templateUrl: 'partials/login.html',
        controller: 'LoginCtrl'
      }).
      when('/reg', {
        templateUrl: 'partials/reg.html',
        controller: 'RegCtrl'
      }).
      when('/wallets/new', {
        templateUrl: 'partials/new-wallet.html',
        controller: 'NewWallet'
      }).
      when('/wallets', {
        templateUrl: 'partials/wallet-list.html',
        controller: 'WalletListCtrl'
      }).
      when('/wallets/:walletId', {
        templateUrl: 'partials/wallet-detail.html',
        controller: 'WalletDetailCtrl'
      }).
      when('/wallets/:walletId/newuser', {
        templateUrl: 'partials/wallet-new-user.html',
        controller: 'WalletNewUserCtrl'
      }).
      when('/wallets/:walletId/newevent', {
        templateUrl: 'partials/wallet-new-event.html',
        controller: 'WalletNewEventCtrl'
      }).
      when('/wallets/:walletId/events/:eventId', {
        templateUrl: 'partials/events.html',
        controller: 'EventDetailCtrl'
      }).
      otherwise({
        redirectTo: '/login'
      });
      var logsOutUserOn401 = ['$q', '$location', function ($q, $location) {
        var success = function (response) {
          return response;
        };

        var error = function (response) {
          if (response.status === 401) {
            //redirect them back to login page
            $location.path('/login');

            return $q.reject(response);
          }
          else {
            return $q.reject(response);
          }
        };

        return function (promise) {
          return promise.then(success, error);
        };
      }];

      $httpProvider.responseInterceptors.push(logsOutUserOn401);

  }]);

shareWalletApp.run(function( $rootScope, $location, TokenHandler) {
 // enumerate routes that don't need authentication
  var routesThatDontRequireAuth = ['/login', '/reg'];

  // check if current location matches route
  var routeClean = function (route) {
    return _.find(routesThatDontRequireAuth,
      function (noAuthRoute) {
        return _.string.startsWith(route, noAuthRoute);
      });
  };

  $rootScope.$on('$routeChangeStart', function (event, next, current) {
    // if route requires auth and user is not logged in
    if (!routeClean($location.url()) && !TokenHandler.isLoggedIn()) {
      // redirect back to login
      $location.path('/login');
    }
  });
});

