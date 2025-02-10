// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "forge-std/Test.sol";
import "../src/GlobalVectorManager.sol";

contract GlobalVectorManagerTest is Test {
    GlobalVectorManager public manager;
    address public admin;
    address public dataNode;

    function setUp() public {
        admin = address(this);
        dataNode = address(0x2);
        manager = new GlobalVectorManager();
        
        // Admin joins the contract
        manager.joinAsAdmin();
        
        // Data node joins the contract
        vm.prank(dataNode);
        manager.joinAsDataNode();
    }

    function testUploadVectorByDataNode() public {
        // Data node uploads a vector
        vm.prank(dataNode);
        manager.uploadVector("QmHashDataNode");

        (string memory ipfsHash, address uploader, uint256 timestamp, bool verified) = manager.getVector(1);
        assertEq(ipfsHash, "QmHashDataNode");
        assertEq(uploader, dataNode);
        assertTrue(timestamp > 0);
        assertFalse(verified);
    }

    function testVerifyVectorByAdmin() public {
        // Data node uploads a vector
        vm.prank(dataNode);
        manager.uploadVector("QmHashDataNode");

        // Admin verifies the vector
        manager.verifyVector(1, true);
        (, , , bool isVerified) = manager.getVector(1);
        assertTrue(isVerified);
    }

    function testIncentivePaidToDataNode() public {
        // Data node uploads a vector
        vm.prank(dataNode);
        manager.uploadVector("QmHashDataNode");

        // Admin verifies the vector
        manager.verifyVector(1, true);

        // Check if incentive was paid (this would require additional logic to track incentives)
        // For example, you could add a mapping to track incentives in the contract and assert here.
    }
}