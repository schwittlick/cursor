from cursor.misc import Timer

import time


if __name__ == "__main__":
    timer = Timer()
    timer.start()

    time.sleep(1)

    print(f"{timer.elapsed()}s")
