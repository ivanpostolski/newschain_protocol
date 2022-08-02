pragma solidity ^0.8.0;

import "OpenZeppelin/openzeppelin-contracts@4.5.0/contracts/utils/math/SafeMath.sol";

import "./INewsChainRoot.sol";

//* A beacon contract to upload and discover new versions of NewsChain contract and frontend */
contract NewsChainRoot {
  address payable owner; 

  
  constructor() {
    owner = payable(msg.sender); 
  }

  uint backend_version = 0;

  event newschain_version(uint indexed api, uint indexed version, address contract_address, string contract_abi);

  event newschain_frontend(uint indexed api,uint indexed version, string endpoint);

  function register_version(uint api, address contract_address, string calldata contract_abi) public {
    require(msg.sender == owner);
    backend_version++;
    emit newschain_version(api,backend_version,contract_address,contract_abi);
  }

  uint frontend_version = 0;

  function register_api_frontend(uint api,string calldata endpoint) public {
    require(msg.sender == owner);
    frontend_version++;
    emit newschain_frontend(api,frontend_version,endpoint);
  }

}