pragma solidity ^0.8.0;

import "OpenZeppelin/openzeppelin-contracts@4.5.0/contracts/utils/math/SafeMath.sol";

import "OpenZeppelin/openzeppelin-contracts@4.5.0/contracts/utils/cryptography/ECDSA.sol";


contract TestUtilityContract {

    function keccak_encode_msg(bytes32 b) public pure returns(bytes32){
        return keccak256(abi.encodePacked("\x19Ethereum Signed Message:\n32",b));
    }

    function keccak_a_b(bytes32 a,bytes32 b) public pure returns(bytes32){
        return keccak256(abi.encodePacked(a,b));
    }

    function keccak_a(string calldata a) public pure returns(bytes32){
        return keccak256(abi.encodePacked(a));
    }

    function recover(bytes calldata challenge, bytes memory signature) public pure returns(address){
        return ECDSA.recover(keccak256(abi.encodePacked("\x19Ethereum Signed Message:\n32",challenge)),signature);
    }

}