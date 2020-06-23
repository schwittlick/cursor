from cursor import loader
from cursor import renderer
from cursor import path
from cursor import filter
from cursor import data
from cursor import device


def main():
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
            print(keys[current_key_index][0], end="")
            current_key_index += 1
        if current_key_index >= len(keys):
            running = False


if __name__ == "__main__":
    main()
