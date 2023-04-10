import json
import random

import requests


def generate_holders_query(contract: str, token: int) -> str:
    return f''' query LatestEvents {{
      tokens_by_pk(fa2_address: "{contract}", token_id: "{token}") {{
        holdings(where: {{amount: {{_gt: "0"}}}}) {{
          holder_address
          amount
        }}
      }}
    }}
    '''


def get_data(query: str) -> dict:
    url = 'https://api.teztok.com/v1/graphql'
    r = requests.post(url, json={'query': query})
    return json.loads(r.text)


def parse(data: dict) -> list[str]:
    holder_addresses = []

    holdings = data["data"]["tokens_by_pk"]["holdings"]
    for holding in holdings:
        address = holding['holder_address']
        amount = holding['amount']
        holder_addresses.extend([address for _ in range(amount)])

    return holder_addresses


def do_raffle() -> None:
    contract = "KT1FRjrFbRbAcJYuXiwJxmQC5sYpHgXbLQ4S"
    query = generate_holders_query(contract, 0)
    data = get_data(query)
    holders = parse(data)

    random.shuffle(holders)

    for idx, holder in enumerate(holders):
        print(f"{holder} 🫴 token id {idx + 1}")


if __name__ == '__main__':
    do_raffle()
