pragma solidity ^0.8.12;

abstract contract INewsChainRoot {

    function get_location_contract(uint location) virtual public view returns(address);

}