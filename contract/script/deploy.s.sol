// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "forge-std/Script.sol";
import "../src/GlobalVectorManager.sol"; 

contract Deploy is Script {
    function run() external {
        vm.startBroadcast();
        new GlobalVectorManager();
        vm.stopBroadcast();
    }
}