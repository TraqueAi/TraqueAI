// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract GlobalVectorManager {
    struct VectorData {
        string ipfsHash;
        address uploader;
        uint256 timestamp;
        bool verified;
    }

    mapping(uint256 => VectorData) public vectors;
    uint256 public vectorCount;
    address public admin;
    mapping(address => bool) public isAdmin;
    mapping(address => bool) public isDataNode;
    address[] public dataNodes;
    address[] public admins;

    event VectorUploaded(uint256 indexed vectorId, string ipfsHash, address indexed uploader, uint256 timestamp);
    event VectorVerified(uint256 indexed vectorId, bool verified);
    event AdminJoined(address indexed admin);
    event DataNodeJoined(address indexed dataNode);
    event IncentivePaid(address indexed dataNode, uint256 amount);

    modifier onlyAdmin() {
        require(isAdmin[msg.sender], "Not an admin");
        _;
    }

    constructor() {
        admin = msg.sender;
        isAdmin[admin] = true;
        admins.push(admin);
        emit AdminJoined(admin);
    }

    function joinAsDataNode() public {
        require(!isDataNode[msg.sender], "Already a data node");
        isDataNode[msg.sender] = true;
        dataNodes.push(msg.sender);
        emit DataNodeJoined(msg.sender);
    }

    function uploadVector(string memory ipfsHash) public {
        require(isDataNode[msg.sender], "Not a data node");
        vectorCount++;
        vectors[vectorCount] = VectorData(ipfsHash, msg.sender, block.timestamp, false);
        emit VectorUploaded(vectorCount, ipfsHash, msg.sender, block.timestamp);
    }

    function joinAsAdmin() public {
        require(!isAdmin[msg.sender], "Already an admin");
        isAdmin[msg.sender] = true;
        admins.push(msg.sender);
        emit AdminJoined(msg.sender);
    }

    function verifyVector(uint256 vectorId, bool isVerified) public onlyAdmin {
        VectorData storage vector = vectors[vectorId];
        vector.verified = isVerified;
        emit VectorVerified(vectorId, isVerified);
        
        if (isVerified) {
            uint256 adminCount = 0;
            for (uint256 i = 0; i < admins.length; i++) {
                if (isAdmin[admins[i]]) {
                    adminCount++;
                }
            }
            if (adminCount * 2 >= admins.length) {
                // Merge vector logic here
                // Incentive logic for data node
                emit IncentivePaid(vector.uploader, 1 ether); // Example incentive
            }
        }
    }

    function getVector(uint256 vectorId) public view returns (string memory, address, uint256, bool) {
        VectorData memory vector = vectors[vectorId];
        return (vector.ipfsHash, vector.uploader, vector.timestamp, vector.verified);
    }

    function leaveContract() public {
        require(isDataNode[msg.sender] || isAdmin[msg.sender], "Not a member");
        if (isDataNode[msg.sender]) {
            isDataNode[msg.sender] = false;
            // Remove from dataNodes array logic here
        } else {
            isAdmin[msg.sender] = false;
            // Remove from admins array logic here
        }
    }
}