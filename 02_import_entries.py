"""
Batch call new contract's migrateAccountEscrowBalances to prepare migration
"""
import csv
import secrets

from eth_account import Account
from web3 import Web3
from web3.datastructures import AttributeDict

import abi
from web3_connection import w3, owner_account, private_key

# migration batch size
BULK_SIZE = 200

reward_escrow_v2_address = "0xeFaA1168A8d4a4DbBD8fE4b2306148badE14958D"

reward_escrow_v2_contract_instance = w3.eth.contract(
    address=reward_escrow_v2_address, abi=abi.reward_escrow_v2
)


def migrate_account_escrow_balances(
    accounts: list, escrow_balances: list, vested_balances: list
):
    # data validate
    assert len(accounts) == len(escrow_balances)
    assert len(accounts) == len(vested_balances)

    # print(accounts)
    # print(escrow_balances)
    # print(vested_balances)
    # return
    print("Account Length:", len(accounts))

    escrow_balances = list(map(lambda x: int(x), escrow_balances))
    vested_balances = list(map(lambda x: int(x), vested_balances))

    nonce = w3.eth.get_transaction_count(owner_account.address)
    print("GAS Price:", w3.eth.gas_price)
    print(
        "Owner Address:",
        owner_account.address,
        "\nBalance:",
        w3.eth.get_balance(owner_account.address),
        "\nNonce:",
        nonce,
    )
    estimate_gas = (
        reward_escrow_v2_contract_instance.functions.migrateAccountEscrowBalances(
            accounts,
            escrow_balances,
            vested_balances,
        ).estimateGas()
    )
    print("Estimate GAS:", estimate_gas, "Actual:", int(estimate_gas))
    migration_txn = (
        reward_escrow_v2_contract_instance.functions.migrateAccountEscrowBalances(
            accounts,
            escrow_balances,
            vested_balances,
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

    tx_status = tx_receipt.get("status")
    print("TX status:", tx_status, "TX detail:", tx_receipt)
    # if failed
    if tx_status != 1:
        print(accounts)
        print(escrow_balances)
        raise Exception(f"Migration failed with status {tx_status} at tx {tx_hash}.")

    # save migrated account
    with open("migrated.csv", "w+") as f:
        csv_writer = csv.writer(f)

        for index, account in enumerate(accounts):
            csv_writer.writerow(
                [account, escrow_balances[index], vested_balances[index]]
            )


with open("old_balances.csv", "r") as f:
    csv_reader = csv.reader(f)

    arg_accounts = []
    arg_escrow_balances = []
    arg_vested_balances = []

    for e in csv_reader:
        account = e[0]
        old_balance = e[1]
        if old_balance == str(0):
            continue

        arg_accounts.append(account)
        arg_escrow_balances.append(int(old_balance))
        arg_vested_balances.append(0)

        # migration
        if len(arg_accounts) >= BULK_SIZE:
            migrate_account_escrow_balances(
                arg_accounts, arg_escrow_balances, arg_vested_balances
            )
            # reset
            arg_accounts = []
            arg_escrow_balances = []
            arg_vested_balances = []

    if len(arg_accounts) > 0:
        migrate_account_escrow_balances(
            arg_accounts, arg_escrow_balances, arg_vested_balances
        )
