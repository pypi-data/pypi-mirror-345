from web3 import Web3, Account as Account
from eth_typing.evm import Address
from web3.types import Wei, TxParams
from eth_utils.conversions import to_hex
from web3.contract.contract import ContractFunction
from web3.contract import Contract
from typing import Optional, Tuple
import requests
import os
from loguru import logger
from pathlib import Path
from .util import to_checksum_address, set_log_level
from bip44 import Wallet
from .proxy import get_dynamic_http_proxy, get_static_http_proxy
from .const import STATUS
from .network import get_rpc, get_chain_id


class EvmAccount:
    name: str
    private_key: str
    w3: Web3
    address: Address
    account: Account
    gas_price_multiplier: float
    gas_limit_multiplier: float
    chain_id: str = None

    def __init__(self,
                 log_level: str = 'INFO',
                 name: str = "default",
                 endpoint_name: str = None,
                 endpoint: str = None,
                 address: str = None,
                 private_key: str = None,
                 gas_price_multiplier: float = None,
                 gas_limit_multiplier: float = None,
                 mnemonic: str = None,
                 address_index: int = 0,
                 chain_id: str = None,
                 use_proxy: bool = False,
                 is_static_proxy: bool = True,
                 proxy: dict = None) -> None:
        set_log_level(log_level)
        if not endpoint_name and not endpoint:
            raise ValueError("rpc config cant be empty")
        if not endpoint:
            endpoint = get_rpc(name=endpoint_name)
            self.chain_id = get_chain_id(name=endpoint_name)
        if chain_id is not None:
            self.chain_id = chain_id
        # if not private_key and not mnemonic:
        #     raise ValueError("private_key or mnemonic cant be empty")
        self.gas_price_multiplier = 1.0
        if gas_price_multiplier is not None:
            self.gas_price_multiplier = gas_price_multiplier
        self.gas_limit_multiplier = 1.0
        if gas_limit_multiplier is not None:
            self.gas_limit_multiplier = gas_limit_multiplier
        self.name = name
        self.w3 = self.init_web3(
            use_proxy=use_proxy,
            is_static_proxy=is_static_proxy,
            proxy=proxy,
            endpoint=endpoint,
        )
        if private_key is not None:
            self.private_key = private_key
            self.account = self.init_account(private_key=private_key)
            self.address = self.account.address
        elif mnemonic is not None:
            self.account = self.init_account_from_mnemonic(
                mnemonic=mnemonic, address_index=address_index)
            self.address = self.account.address
        if private_key is None and mnemonic is None and address is not None:
            self.address = self.init_addr(addr=address)
        logger.info(
            f'wallet_name = {self.name}, wallet_address = {self.address} : init success'
        )

    def log_debug(self, txt: str):
        logger.debug(
            f'wallet_name = {self.name}, wallet_address = {self.address} : {txt}'
        )

    def log_info(self, txt: str):
        logger.info(
            f'wallet_name = {self.name}, wallet_address = {self.address} : {txt}'
        )

    def log_warn(self, txt: str):
        logger.warning(
            f'wallet_name = {self.name}, wallet_address = {self.address} : {txt}'
        )

    def log_err(self, txt: str):
        logger.error(
            f'wallet_name = {self.name}, wallet_address = {self.address} : {txt}'
        )

    def log_fail(self, e):
        self.log_err(f'FAIL : {e}')

    def init_web3(
        self,
        use_proxy,
        is_static_proxy: bool,
        proxy: dict,
        endpoint: str = None,
    ):
        adapter = requests.adapters.HTTPAdapter(pool_connections=20,
                                                pool_maxsize=20,
                                                max_retries=1)
        session = requests.Session()
        if proxy:
            session.proxies = proxy
        elif use_proxy:
            if is_static_proxy == True:
                session.proxies = get_static_http_proxy()
            else:
                session.proxies = get_dynamic_http_proxy()
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        if not endpoint:
            raise ValueError("rpc cant be empty")
        w3_provider = Web3.HTTPProvider(endpoint_uri=endpoint, session=session)
        return Web3(provider=w3_provider)

    def init_account(self, private_key: str) -> Account:
        return Account.from_key(private_key)

    def init_account_from_mnemonic(self, mnemonic: str,
                                   address_index: int) -> Account:
        if not address_index:
            address_index = 0
        wallet = Wallet(mnemonic=mnemonic)
        pk, _ = wallet.derive_account(coin='ETH', address_index=address_index)
        self.private_key = pk.hex()
        return self.init_account(private_key=pk)

    def init_addr(self, addr: str):
        return to_checksum_address(addr)

    def init_contract(self, addr: Address, dir: str,
                      abi_name: str) -> Contract:
        with Path(dir).joinpath(abi_name).open('r') as f:
            abi = f.read()
        return self.init_contract_with_abi_str(addr=addr, abi_str=abi)

    def init_contract_with_abi_str(self, addr: Address, abi_str: str):
        return self.w3.eth.contract(address=addr, abi=abi_str)

    def get_balance(self, address: Address = None):
        if address is None:
            address = self.account.address
        return self.w3.eth.get_balance(address)

    def get_token_balance(self,
                          token_address: Address,
                          address: Address = None):
        if address is None:
            address = self.account.address
        erc20_token = self.init_contract(addr=token_address,
                                         dir=os.path.dirname(__file__),
                                         abi_name='erc20.json')
        return erc20_token.functions.balanceOf(address).call()

    def transfer_token(self, token_address: Address,
                       receipient_address: Address, value: Wei):
        erc20_token = self.init_contract(addr=token_address,
                                         dir=os.path.dirname(__file__),
                                         abi_name='erc20.json')
        f = erc20_token.functions.transfer(receipient_address, value)
        return self.make_tx(f=f)

    def get_nonce(self, address: str = None):
        addr = self.address
        if address is not None:
            addr = address
        return self.w3.eth.get_transaction_count(addr, 'pending')

    def get_gas_price(self) -> Wei:
        gas_price = self.w3.eth.gas_price
        return gas_price

    def get_default_tx_params(self,
                              chain_id: str = None,
                              to: Address = None,
                              data: str = None,
                              val: Wei = Wei(0),
                              gas: Optional[Wei] = None,
                              gas_price: Optional[Wei] = None):

        tx_params: TxParams = {
            'from': self.account.address,
            'value': val,
            'nonce': self.get_nonce()
        }
        if gas is not None:
            tx_params['gas'] = gas
        if gas_price is not None:
            tx_params['gasPrice'] = gas_price
        if to is not None:
            tx_params['to'] = to
        if data is not None:
            tx_params['data'] = data
        if chain_id is not None:
            tx_params['chainId'] = chain_id
        return tx_params

    def sign_tx(self, params: TxParams):
        return self.w3.eth.account.sign_transaction(
            params, private_key=self.private_key)

    def send_tx_and_wait_recipt(self,
                                signed_tx,
                                timeout: int = 120,
                                wait_for_tx: bool = True) -> Tuple:
        try:
            tx = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            txHash = to_hex(tx)
            if wait_for_tx:
                recipt = self.w3.eth.wait_for_transaction_receipt(
                    tx, timeout=timeout)
                if recipt == None:
                    self.log_err(f'tx failed: {txHash}')
                    return None, False
                status = recipt[STATUS]
                if status != 0:
                    self.log_info(f'tx succeeded : {txHash}')
                    return recipt, True
                else:
                    self.log_err(f'tx failed, check it: {txHash}')
                    return recipt, False
            else:
                self.log_info(f'tx generated : {txHash}')
        except Exception as e:
            self.log_err(f'tx exception occurs : {e}')
            return None, False

    def simulate_tx(self,
                    chain_id: str = None,
                    f: ContractFunction = None,
                    gas: Optional[Wei] = None,
                    gas_price: Optional[Wei] = None,
                    to: Address = None,
                    data: str = None,
                    val: Wei = Wei(0)):

        tx_params = self.get_default_tx_params(chain_id=chain_id,
                                               to=to,
                                               data=data,
                                               val=val,
                                               gas=gas,
                                               gas_price=gas_price)
        if gas_price is None:
            gas_price = self.w3.eth.gas_price
            self.log_debug(f'estimated gas price: {gas_price/1e9} GWei')
            tx_params['gasPrice'] = int(self.gas_price_multiplier * gas_price)

        if f is not None:
            tx_params = f.build_transaction(transaction=tx_params)

        if gas is None:
            gas = self.w3.eth.estimate_gas(tx_params)
            self.log_debug(f'estimated gas limit: {gas}')
            tx_params['gas'] = int(gas * self.gas_limit_multiplier)
        self.log_debug(f'[origin] estimated gas fee: {gas_price*gas/1e18}')
        if self.gas_limit_multiplier * self.gas_price_multiplier > 1.01:
            self.log_debug(
                f'[enlarge] estimated gas fee: {self.gas_price_multiplier*gas_price * self.gas_limit_multiplier * gas/1e18}'
            )
        return tx_params

    def make_tx(self,
                chain_id: str = None,
                f: ContractFunction = None,
                gas: Optional[Wei] = None,
                gas_price: Optional[Wei] = None,
                to: Address = None,
                data: str = None,
                val: Wei = Wei(0),
                timeout: int = 120,
                wait_for_tx: bool = True):
        try:
            tx_params = self.simulate_tx(chain_id=chain_id,
                                         f=f,
                                         gas=gas,
                                         gas_price=gas_price,
                                         to=to,
                                         data=data,
                                         val=val)
        except Exception as e:
            self.log_err(f'tx simulated failed, err = {e}')
            return None, False
        signed_tx = self.sign_tx(params=tx_params)
        return self.send_tx_and_wait_recipt(signed_tx=signed_tx,
                                            timeout=timeout,
                                            wait_for_tx=wait_for_tx)


if __name__ == '__main__':

    sepolia_test_pk = '0xxxxxxxx'
    from .const import SEPOLIA
    wallet = EvmAccount(private_key=sepolia_test_pk, endpoint_name=SEPOLIA)

    nonce = wallet.get_nonce()
    wallet.log_info(f'nonce = {nonce}')

    gas_price = wallet.get_gas_price()
    wallet.log_info(f'gas_price = {round(gas_price/1e9,2)} GWei')
    from .util import to_checksum_address
    wallet.simulate_tx(
        to=to_checksum_address('0x5c9b7a5c7c8e5f4c5a8e5f4c5a8e5f4c5a8e5f4d'),
        val=Web3.to_wei(0.0001, 'ether'))

    wallet.make_tx(
        to=to_checksum_address('0x5c9b7a5c7c8e5f4c5a8e5f4c5a8e5f4c5a8e5f4d'),
        val=Web3.to_wei(0.0001, 'ether'))
