pragma solidity =0.5.16;

import '../MuesliERC20.sol';

contract ERC20 is MuesliERC20 {
    constructor(uint _totalSupply) public {
        _mint(msg.sender, _totalSupply);
    }
}
