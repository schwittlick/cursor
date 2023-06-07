import json

if __name__ == '__main__':
    """
    parses json from teztok https://graphiql.teztok.com/
    prints only relevant data to
    be pasted into gdoc

    query LatestEvents {
      tokens_by_pk(fa2_address: "KT1FRjrFbRbAcJYuXiwJxmQC5sYpHgXbLQ4S", token_id: "0") {
        editions
        offers(where: {status: {_eq: "active"}}) {
          price
          status
          buyer_address
          buyer_profile {
            alias
          }
        }
      }
    }
    """
    data = json.load(open("raffle.json"))
    offers = data["data"]["tokens_by_pk"]["offers"]
    for offer in offers:
        profile = offer['buyer_profile']
        alias = "None"
        if profile:
            alias = profile["alias"]
        price = offer['price'] / 1000000
        out = f"{price};{offer['buyer_address']};{alias} "
        print(out)
