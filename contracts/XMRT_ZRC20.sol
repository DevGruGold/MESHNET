// SPDX-License-Identifier: MIT
pragma solidity 0.8.26;

import "@zetachain/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol";
import "@zetachain/protocol-contracts/contracts/zevm/interfaces/IGatewayZEVM.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

/**
 * @title XMRT_ZRC20
 * @dev ZRC20 implementation of XMRT token for cross-chain operations
 * Enables seamless bridging between ZetaChain and all connected blockchains
 */
contract XMRT_ZRC20 is IZRC20, ERC20, AccessControl, Pausable {

    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    bytes32 public constant GATEWAY_ROLE = keccak256("GATEWAY_ROLE");
    bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");

    IGatewayZEVM public immutable gateway;
    uint256 public protocolFee;

    mapping(address => bool) public authorizedMinters;
    mapping(uint256 => address) public chainTokenAddresses;

    event CrossChainTransfer(
        address indexed from,
        address indexed to,
        uint256 amount,
        uint256 destinationChain
    );

    event TokenMinted(
        address indexed to,
        uint256 amount,
        string reason
    );

    event ChainTokenSet(
        uint256 indexed chainId,
        address indexed tokenAddress
    );

    constructor(
        address _gateway,
        uint256 _protocolFee
    ) ERC20("XMRT Cross-Chain", "XMRT") {
        gateway = IGatewayZEVM(_gateway);
        protocolFee = _protocolFee;

        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(MINTER_ROLE, msg.sender);
        _grantRole(GATEWAY_ROLE, _gateway);
        _grantRole(PAUSER_ROLE, msg.sender);
    }

    /**
     * @dev Mint XMRT tokens for mining rewards
     */
    function mintReward(
        address to,
        uint256 amount,
        string calldata reason
    ) external onlyRole(MINTER_ROLE) whenNotPaused {
        _mint(to, amount);
        emit TokenMinted(to, amount, reason);
    }

    /**
     * @dev Withdraw tokens to specific chain
     */
    function withdraw(
        bytes memory to,
        uint256 amount
    ) external override returns (bool) {
        return withdrawToChain(to, amount, 1); // Default to Ethereum
    }

    /**
     * @dev Withdraw tokens to specific chain with chain ID
     */
    function withdrawToChain(
        bytes memory to,
        uint256 amount,
        uint256 chainId
    ) public returns (bool) {
        require(amount > 0, "Amount must be greater than 0");
        require(balanceOf(msg.sender) >= amount, "Insufficient balance");

        // Burn tokens from sender
        _burn(msg.sender, amount);

        // Calculate fees
        uint256 fee = (amount * protocolFee) / 10000;
        uint256 netAmount = amount - fee;

        // Use gateway to withdraw to destination chain
        RevertOptions memory revertOptions = RevertOptions({
            revertAddress: msg.sender,
            callOnRevert: false,
            abortAddress: msg.sender,
            revertMessage: "",
            onRevertGasLimit: 0
        });

        gateway.withdrawAndCall(
            to,
            netAmount,
            address(this),
            "",
            revertOptions,
            chainId
        );

        emit CrossChainTransfer(msg.sender, address(0), netAmount, chainId);
        return true;
    }

    /**
     * @dev Get protocol fee for withdrawal
     */
    function withdrawGasFee() external view override returns (address, uint256) {
        return (address(this), protocolFee);
    }

    /**
     * @dev Set protocol fee
     */
    function setProtocolFee(uint256 _protocolFee) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(_protocolFee <= 1000, "Fee too high"); // Max 10%
        protocolFee = _protocolFee;
    }

    /**
     * @dev Set token address for specific chain
     */
    function setChainTokenAddress(
        uint256 chainId,
        address tokenAddress
    ) external onlyRole(DEFAULT_ADMIN_ROLE) {
        chainTokenAddresses[chainId] = tokenAddress;
        emit ChainTokenSet(chainId, tokenAddress);
    }

    /**
     * @dev Pause contract
     */
    function pause() external onlyRole(PAUSER_ROLE) {
        _pause();
    }

    /**
     * @dev Unpause contract
     */
    function unpause() external onlyRole(PAUSER_ROLE) {
        _unpause();
    }

    /**
     * @dev Override transfer to add pause functionality
     */
    function transfer(
        address to,
        uint256 amount
    ) public override whenNotPaused returns (bool) {
        return super.transfer(to, amount);
    }

    /**
     * @dev Override transferFrom to add pause functionality
     */
    function transferFrom(
        address from,
        address to,
        uint256 amount
    ) public override whenNotPaused returns (bool) {
        return super.transferFrom(from, to, amount);
    }
}