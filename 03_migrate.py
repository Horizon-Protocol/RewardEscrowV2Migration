"""
Import account's Vesting Schedule
"""
import csv

from web3 import Web3
from web3.datastructures import AttributeDict

import abi
from web3_connection import w3, owner_account

reward_escrow_v2_address = "0xeFaA1168A8d4a4DbBD8fE4b2306148badE14958D"

reward_escrow_v2_contract_instance = w3.eth.contract(
    address=reward_escrow_v2_address, abi=abi.reward_escrow_v2
)


print(
    "Owner Address:",
    owner_account.address,
    "\nBalance:",
    w3.eth.get_balance(owner_account.address),
)

with open("migrated.csv", "r") as f:
    csv_reader = csv.reader(f)

    for a in csv_reader:
        address = a[0]
        print("Migrate Rewards Escrow For Wallet:", address)
        nonce = w3.eth.get_transaction_count(owner_account.address)
        estimate_gas = (
            reward_escrow_v2_contract_instance.functions.migrateVestingSchedule(
                address,
            ).estimateGas()
        )
        print("Estimate GAS:", estimate_gas)
        migration_txn = (
            reward_escrow_v2_contract_instance.functions.migrateVestingSchedule(
                address,
            ).buildTransaction(
                {
                    "from": owner_account.address,
                    "gas": estimate_gas,
                    "gasPrice": Web3.toWei(10, "gwei"),
                    "nonce": nonce,
                    "chainId": 97,
                }
            )
        )
        signed_txn = owner_account.sign_transaction(migration_txn)
        w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        tx_hash = w3.toHex(w3.keccak(signed_txn.rawTransaction))
        print("TX hash:", tx_hash)
        tx_receipt: AttributeDict = w3.eth.wait_for_transaction_receipt(tx_hash)
