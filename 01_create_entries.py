"""
Get account escrowed balance and exclude zero balance
"""
import csv

from web3 import Web3

import abi
from web3_connection import w3

with open("accounts.csv", "r") as f:
    account_list = f.read().split("\n")

old_reward_escrow_address = "0xf896D21C72C295E9e6c1DbeC0BEE4Da5380754e5"

old_reward_escrow_contract_instance = w3.eth.contract(
    address=old_reward_escrow_address, abi=abi.old_reward_escrow
)

with open("old_balances.csv", "w+") as f:
    csv_writer = csv.writer(f)

    for a in account_list:
        if not a:
            continue
        account_address = Web3.toChecksumAddress(a)
        num_entries = old_reward_escrow_contract_instance.functions.numVestingEntries(
            account_address
        ).call()
        line_detail = [account_address]
        old_balance = old_reward_escrow_contract_instance.functions.balanceOf(
            account_address
        ).call()
        line_detail.append(old_balance)
        # for e in range(num_entries):
        #     print(e)
        #     vesting_schedule = old_reward_escrow_contract_instance.functions.getVestingScheduleEntry(a, e).call()
        #     line_detail.append(vesting_schedule[1])
        #     print(vesting_schedule)

        csv_writer.writerow(line_detail)

        print(account_address, old_balance / 10 ** 18)
