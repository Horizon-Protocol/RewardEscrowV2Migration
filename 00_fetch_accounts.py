"""
Create minted accounts list
"""
import requests


class Query:
    @staticmethod
    def string(first, skip):
        return """ {
          snxholders(first: %s, orderBy:timestamp, orderDirection: desc, subgraphError: deny, skip: %s) {
            id
          }
        } """ % (
            first,
            skip,
        )


accounts = []

first = 1000
skip = 0
while True:
    resp = requests.post(
        "https://graphnode.horizonprotocol.com/subgraphs/name/horizonprotocol-team/horizon",
        json={
            "query": Query.string(first=first, skip=skip),
            "variables": None,
            "operationName": None,
        },
    )
    print(first, skip)

    snx_holders = resp.json()["data"]["snxholders"]
    for i in snx_holders:
        # print(i['id'])
        accounts.append(i["id"])
    if len(snx_holders) < first:
        break

    skip += first

accounts = list(set(accounts))
print(len(accounts))

with open("accounts.csv", "w+") as f:
    f.write("\n".join(accounts))
