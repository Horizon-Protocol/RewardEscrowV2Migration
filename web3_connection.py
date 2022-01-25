from eth_account.signers.base import BaseAccount
from web3 import Web3
from web3.middleware import geth_poa_middleware


# BSC mainnet
# w3 = Web3(Web3.HTTPProvider('https://bsc-dataseed4.defibit.io/'))
# BSC testnet
w3 = Web3(Web3.HTTPProvider("https://data-seed-prebsc-1-s1.binance.org:8545/"))
# Support bsc poa chain
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

private_key = "0xYourPrivateKey"
owner_account: BaseAccount = w3.eth.account.from_key(private_key)
w3.eth.default_account = owner_account.address
