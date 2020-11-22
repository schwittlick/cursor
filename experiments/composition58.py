from cursor import loader
from cursor import data

import time
from pythonosc import udp_client


# This is c58 which is using keys to control synthesizers in supercollider
# no mouse lines used in this script


def main():
    client = udp_client.SimpleUDPClient("127.0.0.1", 57120)
    # this port needs to be taken from SC via NetAddr.langPort;

    p = data.DataDirHandler().recordings()
    p = p.joinpath("1594553245.575756_compressed.json")
    ll = loader.Loader()
    ll.load_file(p)
    keys = ll.keys()
    print(len(keys))

    # start_time = data.DateHandler.get_timestamp_from_utc(keys[0][1])
    # end_time = data.DateHandler.get_timestamp_from_utc(keys[-1][1])

    diff = data.DateHandler.utc_timestamp() - keys[0][1]

    running = True
    current_key_index = 0
    while running is True:

        ts = data.DateHandler.utc_timestamp() - diff
        if ts > keys[current_key_index][1]:
            k = keys[current_key_index][0]
            down = keys[current_key_index][2]
            print(down)
            # print(k)
            if down:
                try:
                    client.send_message("/keyboard_keys_ascii", ord(k))
                except:
                    client.send_message("/keyboard_keys_ascii_special", k)

            current_key_index += 1
        if current_key_index >= len(keys) - 1:
            running = False
        time.sleep(0.001)

    print("done")


if __name__ == "__main__":
    main()
