import json
import random

import requests


def generate_holders_query(contract: str, token: int):
    return f''' query LatestEvents {{
      tokens_by_pk(fa2_address: "{contract}", token_id: "{token}") {{
        holdings(where: {{amount: {{_gt: "0"}}}}) {{
          holder_address
          holder_profile {{
            alias
          }}
          amount
        }}
      }}
    }}
    '''


def get_data(query: str):
    url = 'https://api.teztok.com/v1/graphql'
    r = requests.post(url, json={'query': query})
    return json.loads(r.text)


def parse(data: dict):
    holder_addresses = []

    holdings = data["data"]["tokens_by_pk"]["holdings"]
    for holding in holdings:
        address = holding['holder_address']
        profile = holding['holder_profile']
        if profile:
            address = f"{address} {profile['alias']}"
        amount = holding['amount']
        holder_addresses.extend([address for _ in range(amount)])

    return holder_addresses


def do_raffle():
    contract = "KT1FRjrFbRbAcJYuXiwJxmQC5sYpHgXbLQ4S"
    query = generate_holders_query(contract, 0)
    data = get_data(query)
    holders = parse(data)

    token_ids = list(range(1, len(holders) + 1))

    for id in token_ids:
        random_holder_idx = random.randrange(len(holders))
        random_holder = holders.pop(random_holder_idx)

        print(f"{id} -> {random_holder}")


if __name__ == '__main__':
    do_raffle()
