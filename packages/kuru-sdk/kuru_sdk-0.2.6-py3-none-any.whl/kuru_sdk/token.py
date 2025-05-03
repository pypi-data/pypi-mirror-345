from web3 import Web3
from typing import Optional
from decimal import Decimal
import json
from pathlib import Path

class TokenError:
    class ApprovalError(Exception):
        pass
    class TransferError(Exception):
        pass
    class ContractError(Exception):
        pass

class Token:
    def __init__(
        self,
        web3: Web3,
        contract_address: str,
        private_key: Optional[str] = None
    ):
        """
        Initialize the Token interface
        
        Args:
            web3: Web3 instance
            contract_address: Address of the ERC20 token contract
            private_key: Private key for signing transactions (optional)
        """
        self.web3 = web3
        self.contract_address = Web3.to_checksum_address(contract_address)
        self.private_key = private_key
        
        # Load ABI from JSON file
        abi_path = Path(__file__).parent / 'abi' / 'ierc20.json'
        with open(abi_path, 'r') as f:
            contract_abi = json.load(f)
        
        self.contract = self.web3.eth.contract(
            address=self.contract_address,
            abi=contract_abi
        )
        
        # Cache token metadata
        self._name = None
        self._symbol = None
        self._decimals = None

    @property
    def name(self) -> str:
        """Get token name"""
        if self._name is None:
            self._name = self.contract.functions.name().call()
        return self._name

    @property
    def symbol(self) -> str:
        """Get token symbol"""
        if self._symbol is None:
            self._symbol = self.contract.functions.symbol().call()
        return self._symbol

    @property
    def decimals(self) -> int:
        """Get token decimals"""
        if self._decimals is None:
            self._decimals = self.contract.functions.decimals().call()
        return self._decimals

    def format_units(self, amount: int) -> Decimal:
        """
        Convert raw token amount to decimal representation
        
        Args:
            amount: Raw token amount (in wei/smallest unit)
            
        Returns:
            Decimal: Formatted amount
        """
        return Decimal(str(amount)) / Decimal(str(10 ** self.decimals))

    def parse_units(self, amount: str) -> int:
        """
        Convert decimal amount to raw token units
        
        Args:
            amount: Amount in decimal format
            
        Returns:
            int: Amount in raw units
        """
        return int(Decimal(amount) * Decimal(str(10 ** self.decimals)))

    def balance_of(self, address: str) -> int:
        """
        Get token balance of an address
        
        Args:
            address: Address to check balance for
            
        Returns:
            int: Token balance in raw units
        """
        address = Web3.to_checksum_address(address)
        return self.contract.functions.balanceOf(address).call()

    def allowance(self, owner: str, spender: str) -> int:
        """
        Get amount of tokens approved for a spender
        
        Args:
            owner: Token owner address
            spender: Spender address
            
        Returns:
            int: Approved amount in raw units
        """
        owner = Web3.to_checksum_address(owner)
        spender = Web3.to_checksum_address(spender)
        return self.contract.functions.allowance(owner, spender).call()

    def approve(
        self,
        spender: str,
        amount: int,
        from_address: str
    ) -> str:
        """
        Approve spender to spend tokens
        
        Args:
            spender: Spender address
            amount: Amount to approve (in raw units)
            from_address: Address sending the approval
            
        Returns:
            str: Transaction hash
        """
        spender = Web3.to_checksum_address(spender)
        from_address = Web3.to_checksum_address(from_address)
        
        # Build transaction
        transaction = self.contract.functions.approve(spender, amount)
        
        try:
            # Get gas estimate
            gas_estimate = transaction.estimate_gas({'from': from_address})
            
            # Get nonce
            nonce = self.web3.eth.get_transaction_count(from_address)
            
            # Build transaction dict
            transaction_dict = {
                'from': from_address,
                'nonce': nonce,
                'gas': gas_estimate,
                'maxFeePerGas': self.web3.eth.max_priority_fee,
                'maxPriorityFeePerGas': self.web3.eth.max_priority_fee
            }
            
            if self.private_key:
                # Sign and send transaction
                raw_transaction = transaction.build_transaction(transaction_dict)
                signed_txn = self.web3.eth.account.sign_transaction(
                    raw_transaction,
                    self.private_key
                )
                tx_hash = self.web3.eth.send_raw_transaction(signed_txn.raw_transaction)
            else:
                # Let wallet handle signing
                tx_hash = transaction.transact(transaction_dict)
                
            return tx_hash.hex()
            
        except Exception as e:
            raise TokenError.ApprovalError(f"Failed to approve tokens: {str(e)}")
