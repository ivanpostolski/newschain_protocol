pragma solidity ^0.8.0;

import "OpenZeppelin/openzeppelin-contracts@4.5.0/contracts/utils/math/SafeMath.sol";

import "OpenZeppelin/openzeppelin-contracts@4.5.0/contracts/utils/cryptography/ECDSA.sol";

import "./INewsChainRoot.sol";

contract NewsChainContractv0 {

  address payable owner; 

  uint article_counter = 0;
 
  constructor() {
    owner = payable(msg.sender); 
  }

  function getOwner() public view returns(address){
    return owner;
  }

  //** Publication functionality */

  event published_article(uint indexed id, uint indexed location_index,string title, string img,string article,address indexed author,bytes32 challenge);

  ///@notice the mapping of an article to a challenge hash. That is a 32 bytes hash used to provide a secure edition mechanism for published articles
  mapping(uint => bytes32) article_challenge;

  ///@notice the mapping of an article to the block where it was published
  mapping(uint => uint) article_block;

  ///@notice the mapping of an article to its reported location
  mapping(uint => string) article_location;

  ///@notice publishes an article to the blockchain 
  ///@dev a continuation hash is calculated, considering the sender, the block number and the miner address  
  ///@param title the article's title
  ///@param img the aricle's main image
  ///@param article the aricle's initial text (html)
  ///@return a continuation_hash that must be signed with the author privatekey to continue the article writing, plus viewership validation   
  function publish(string calldata title, string calldata img, string calldata article, string calldata location) public returns(bytes32) {
    uint this_article_id = article_counter++;
    bytes32 continuation_hash = keccak256(abi.encodePacked(msg.sender,block.number,block.coinbase));
    article_challenge[this_article_id] = continuation_hash;
    article_pow[this_article_id] = continuation_hash;
    article_block[this_article_id] = block.number;
    article_location[this_article_id] = location;
    emit published_article(this_article_id,uint(keccak256(abi.encodePacked(location))),title,img,article,msg.sender,continuation_hash);
    return continuation_hash;
  }

  
  event article_continuation(uint indexed id,string changes,bytes32 challenge);


  ///@notice continuates a published article  
  ///@param article_id the article id 
  ///@param changes the aricle's continuation text
  ///@param signature the proof of article property
  ///@return a continuation_hash that must be signed with the author privatekey to continue the article writing
  function continue_article(uint article_id, string calldata changes,bytes calldata signature) public returns(bytes32) {
    require(msg.sender == ECDSA.recover(keccak256(abi.encodePacked("\x19Ethereum Signed Message:\n32",article_challenge[article_id])),signature));
    article_challenge[article_id] = keccak256(abi.encodePacked(article_challenge[article_id],block.number,block.coinbase));
    emit article_continuation(article_id,changes,article_challenge[article_id]);
    return article_challenge[article_id];
  }

  //** Open access functionality */

  event plainAccess(uint256 data);


  ///@notice donateAccess function publishes a funded account to allow usability of the contract for users that do not have funds.
  ///@dev requires that sender is the owner of the contract. 
  ///@param account a fresh account address 
  ///@param key the private key of the account parameter
  function donateAccess(address account, uint256 key) public payable returns(bool) {
    require(msg.sender == owner);
    (bool success,) = account.call{value: msg.value}("");
    require(success);
    emit plainAccess(key);
    return true;
  }


  /** Viewership counting functionality */

  /** The objetive is to be able to estimate views of an article per a time unit (e.g hrs) by counting views with transactions event. There are two challenges in this section: 1) avoid producing too many transactions, thus somehow minimizing the gas costs. 2) don't have long delays (low sensitivity) to report the estimated audience. The top-level idea is to make viewers solve a hash riddle, and assuming a computing power of a regular computer, estimate the number of viewers that are out there reading the article.*/

  ///@notice a mapping between article_id and a byte32 hash that has to be processed to prove an article viewership event  
  mapping(uint => bytes32) article_pow;

  ///@notice the current article difficulty that determines the condition a hash must met to be considered as a viewership event (e.g number of leading zeroes) 
  mapping(uint => uint8) article_difficulty;

  ///@notice public function to access current article difficulty level 
  function getArticleDifficulty(uint article_id) public view returns (uint8){
    return article_difficulty[article_id];
  }

  ///@notice Internal function to validate pow of viewership, designed with the following goals: sensitivity of powers of 10 #viewers should be detected within 2 minutes, and with only 2 events (transactions). Assuming a low computing power of 50000 h/s. This is to optimize UX and minimize number of transactions.
  ///@param difficulty the article current viewership pow difficulty
  ///@param challenge the aricle's current challenge hash
  ///@param pow the submitted pow 
  function article_validator(uint8 difficulty, bytes32 challenge, bytes32 pow) private view returns (bool){
    return (bytes5(keccak256(abi.encodePacked(challenge,pow))) & difficulty_masks[difficulty]) <= difficulty_thresholds[difficulty];
  }

  ///@notice byte masks for difficulty checks (number of required leading zeroes) 
  bytes5[6] difficulty_masks = [bytes5(0xFFFFFF0000),bytes5(0xFFFFFFF000),bytes5(0xFFFFFFFF00),bytes5(0xFFFFFFFF00),bytes5(0xFFFFFFFFF0),bytes5(0xFFFFFFFFFF)];

  ///@notice a getter for client retrieval of mask per difficulty level. 
  function getDifficultyMask(uint8 difficulty) public view returns (bytes5){
    return difficulty_masks[difficulty];
  }

  ///@notice additional thresholds to balance the hash riddle difficulty. After complying with the leading zeroes, the following byte must be less than the specified threshold per difficutly level.
  bytes5[6] difficulty_thresholds = [bytes5(0x0000030000),bytes5(0x0000003000),bytes5(0x0000000800),bytes5(0x0000000000),bytes5(0x0000000000),bytes5(0x0000000000)];

  ///@notice a getter for client retrieval of threshold per difficulty level. 
  function getDifficultyThreshold(uint8 difficulty) public view returns (bytes5){
    return difficulty_thresholds[difficulty];
  }

  ///@notice a map that records the last block with a view event of an article.
  mapping(uint => uint) article_last_block_view;

  ///@notice a map that records the last hash that must be used for reporting the pow. 
  mapping(uint => bytes32) article_last_pow;

  ///@notice a map that records the current article deadline block (where the article difficulty level is downgraded)
  mapping(uint => uint) article_deadline_block;

  ///@notice blockchain windows offsets (assuming a block is mined every 15 seconds)  
  uint8 difficulty_window = 40;
  uint8 block_window = 8;
  uint8 up_threshold = 2;
  uint view_window = 4*60*6;

  ///@notice  a getter for client retrieval of the viewer window. 
  function getViewerWindows() public view returns (uint8){
    return block_window;
  }

  ///@notice  a getter for client retrieval of the threshold of view events required to upgrade the current difficulty level.
  function getViewerUpThreshold() public view returns (uint8){
    return up_threshold;
  }

  ///@notice a viewer event that solved the artcle hash riddle, with the location for indexing purposes (rapidly finding the last viewer events), the current article pow (that might have changed as a consecuense of difficulty upgrade), and the current difficulty level (raw estimation of viewership counting).   
  event viewerEvent(uint indexed article_id, string location, uint256 indexed location_index, bytes32 currentPow,uint8 indexed difficulty_level, bool restart);

  ///@notice a transaction to register a viewer event
  ///@param article_id the article that is reported 
  ///@param pow the riddle solution found by a viewer
  function viewer_pow(uint article_id, bytes32 pow) public returns(bytes32){
    require(article_id <= article_counter);
    require(block.number < (article_block[article_id] + view_window));
    uint8 difficulty = article_difficulty[article_id];
    require(article_validator(difficulty,article_pow[article_id],pow),"wrong PoW");
    require(article_last_pow[article_id] != pow, "Duplicated Pow");
    article_last_pow[article_id] = pow;
    uint article_last_block = article_last_block_view[article_id];
    
    if (difficulty > 0 && block.number > article_deadline_block[article_id]) {
        //The article's current difficulty deadline block has expired 
        article_difficulty[article_id]--;
        article_deadline_block[article_id] = block.number + difficulty_window;
        article_pow[article_id] = keccak256(abi.encodePacked(block.number,block.coinbase,pow));
        article_last_block_view[article_id] = 0;
        emit viewerEvent(article_id,article_location[article_id],uint(keccak256(abi.encodePacked(article_location[article_id]))),article_pow[article_id],article_difficulty[article_id],true);
        return article_pow[article_id];
    }
  
    if (article_last_block_view[article_id] > 0 && (block.number - article_last_block) <= block_window){
        //Two events had happen in the block window within the same difficulty, thus the article has to increase its difficulty
        article_difficulty[article_id]++;
        article_pow[article_id] = keccak256(abi.encodePacked(block.number,block.coinbase,pow));
        article_last_block_view[article_id] = 0;
        article_deadline_block[article_id] = block.number + difficulty_window;
        emit viewerEvent(article_id,article_location[article_id],uint(keccak256(abi.encodePacked(article_location[article_id]))),article_pow[article_id],article_difficulty[article_id],true);
    } else {
        //There is not evidence of two events in the same block_window, but difficulty window has not expired yet, thus refresh last block, but keep current pow challenge  
        article_last_block_view[article_id] = block.number;
        emit viewerEvent(article_id,article_location[article_id],uint(keccak256(abi.encodePacked(article_location[article_id]))),article_pow[article_id],article_difficulty[article_id],false);
    }

    
    return article_pow[article_id];
  }

}