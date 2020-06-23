from cursor import loader
from cursor import renderer
from cursor import path
from cursor import filter
from cursor import data
from cursor import device

import time
from pythonosc import udp_client


def main():
    client = udp_client.SimpleUDPClient("127.0.0.1", 57120)

    p = data.DataDirHandler().recordings()
    p = p.joinpath("1592909088.66943_compressed.json")
    ll = loader.Loader()
    ll.load_file(p)
    keys = ll.keys()
    print(len(keys))

    start_time = data.DateHandler.get_timestamp_from_utc(keys[0][1])
    end_time = data.DateHandler.get_timestamp_from_utc(keys[-1][1])

    diff = data.DateHandler.utc_timestamp() - keys[0][1]

    running = True
    current_key_index = 0
    while running is True:
        ts = data.DateHandler.utc_timestamp() - diff
        if ts > keys[current_key_index][1]:
            k = keys[current_key_index][0]
            print(k, end="")
            client.send_message("/hello", ord(k))
            current_key_index += 1
        if current_key_index >= len(keys):
            running = False

    print("done")


if __name__ == "__main__":
    main()
