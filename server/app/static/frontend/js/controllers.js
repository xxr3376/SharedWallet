'use strict';

/* Controllers */
var loginControllers = angular.module('LoginControllers', []);

loginControllers.controller('LoginCtrl', ['$scope', 'TokenHandler', '$location',
  function($scope, tokenHandler, $location) {
    $scope.login = function() {
      tokenHandler.login($scope.username, $scope.password).
        then(function() {
          $location.path('/wallets');
        }, function (reason) {
          alert(reason.data.status);
        });
    };
  }
]);
loginControllers.controller('RegCtrl', ['$scope', 'TokenHandler', '$location', 'Users',
  function($scope, tokenHandler, $location, Users) {
    $scope.reg = function() {
      if (!_.every([$scope.username, $scope.password, $scope.repeat_password, $scope.name])) {
        return;
      }
      if ($scope.password != $scope.repeat_password) {
        alert('两次输入的密码不同');
        return;
      }
      var data = {
        name: $scope.name,
        username: $scope.username,
        password: $scope.password,
      };
      var newUser = new Users(data);
      newUser.$save(function(e) {
        tokenHandler.login($scope.username, $scope.password).
          then(function() {
            $location.path('/wallets');
          }, function (reason) {
            alert(reason.data.status);
          });
      }, function(e) {
        if (e.status == 409) {
          alert('用户名或姓名重复');
        }
        else {
          alert('数据错误');
        }
      });
    };
  }
]);


var shareWalletControllers= angular.module('ShareWalletControllers', []);

shareWalletControllers.controller('WalletListCtrl', ['$scope', 'Wallet',
  function($scope, Wallet) {
    $scope.wallets = Wallet.query();
  }
]);

shareWalletControllers.controller('WalletDetailCtrl', ['$scope', '$routeParams', 'Wallet', 'WalletUser', 'WalletEvent',
  function($scope, $routeParams, Wallet, WalletUser, WalletEvent) {
    $scope.wallet = Wallet.get({walletId: $routeParams.walletId});
    $scope.users = WalletUser.query({walletId: $routeParams.walletId});
    $scope.events = WalletEvent.query({walletId: $routeParams.walletId});
}]);
shareWalletControllers.controller('WalletNewUserCtrl', ['$scope', '$routeParams', 'Users', 'WalletUser', '$location',
  function($scope, $routeParams, Users, WalletUser, $location) {
    $scope.allusers = Users.query();

    $scope.addUser = function(user) {
      var n = new WalletUser({user_id: user.id});
      n.$save({walletId: $routeParams.walletId});
      $location.path('/wallets/' + $routeParams.walletId);
    };
}]);
shareWalletControllers.controller('WalletNewEventCtrl', ['$scope', '$routeParams', 'WalletUser', 'WalletEvent', '$location',
  function($scope, $routeParams, WalletUser, WalletEvent, $location) {
    $scope.users = WalletUser.query({walletId: $routeParams.walletId});
    $scope.payList = {};
    $scope.borrowList = {};
    $scope.borrowRateList = {};
    $scope.customList = {};
    $scope.notes = {};
    $scope.all = {};
    $scope.users.$promise.then(function(list) {
      for (var i = 0; i < list.length; i++) {
        var id = list[i].id;
        $scope.payList[id] = 0;
        $scope.borrowList[id] = 0;
        $scope.borrowRateList[id] = 0;
        $scope.customList[id] = false;
        $scope.notes[id] = '';
        $scope.all[id] = 0;
      }
    });
    $scope.totalPay = function() {
      var total = 0.0;
      for (var id in $scope.payList) {
        total += $scope.payList[id];
      }
      return total;
    };
    $scope.totalBorrow = function() {
      var total = 0.0;
      for (var id in $scope.borrowList) {
        total += $scope.borrowList[id];
      }
      return total;
    };
    $scope.vaild = function() {
      if (Math.abs($scope.totalPay() - $scope.totalBorrow()) < 0.01) {
        return true;
      }
      return false;
    };
    $scope.switchCustom = function(user) {
      $scope.customList[user.id] ^= 1;
      $scope.calculate();
    }
    $scope.calculate = function() {
      var total = $scope.totalPay();
      var totalRate = 0;
      for (var id in $scope.customList) {
        if ($scope.customList[id]) {
          total -= $scope.borrowList[id];
        }
        else {
          totalRate += $scope.borrowRateList[id];
        }
      }
      if (totalRate != 0) {
        for (var id in $scope.customList) {
          if (!$scope.customList[id]) {
            $scope.borrowList[id] = total / totalRate * $scope.borrowRateList[id];
          }
        }
      }
      for (var id in $scope.all) {
        $scope.all[id] = $scope.payList[id] - $scope.borrowList[id];
      }
    };
    $scope.submit = function() {
      if (!$scope.name) {
        alert('请填写名称');
        return;
      }
      if (!$scope.description) {
        alert('请填写描述');
        return;
      }
      var data = {
        name: $scope.name,
        description: $scope.description,
        transaction: [],
      };
      for (var id in $scope.all) {
        if (Math.abs($scope.all[id]) > 0.005) {
          var tmp = {user_id: id};
          tmp.amount = $scope.all[id];
          tmp.notes = $scope.notes[id];
          data.transaction.push(tmp);
        }
      }
      var newEvent = new WalletEvent(data);
      newEvent.$save({walletId: $routeParams.walletId});
      $location.path('/wallets/' + $routeParams.walletId);
    };
}]);
shareWalletControllers.controller('EventDetailCtrl', ['$scope', '$routeParams', 'WalletEvent',
  function($scope, $routeParams, WalletEvent) {
    $scope.walletEvent = WalletEvent.get({walletId: $routeParams.walletId, eventId: $routeParams.eventId});
}]);
shareWalletControllers.controller('NewWallet', ['$scope', 'Wallet', '$location',
  function($scope, Wallet, $location) {
    $scope.submit = function() {
      var newWallet = new Wallet({
        name: $scope.name,
        description: $scope.description,
      });
      newWallet.$save(function() {
        $location.path('/wallets');
      });
    };
}]);


shareWalletControllers.filter('role', function() {
  return function(input) {
    return input == 2 ? '管理员' : '普通用户';
  };
});
