import time
import logging

import pyttsx3

from cursor.tools.discovery import discover

engine = pyttsx3.init()


def check_diff(prev: set[tuple[str, str]], current: set[tuple[str, str]]) -> None:
    diff = prev.symmetric_difference(current)
    for element in diff:
        if element in prev:
            logging.info(f"removed {element}")
            engine.say(f"Removed {element[1]}")
            engine.runAndWait()
        if element in current:
            logging.info(f"added {element}")
            engine.say(f"Added {element[1]}")


if __name__ == "__main__":
    """
    This is a realtime version of the discovery tool.
    """

    discovered = set()
    while True:
        time.sleep(1)
        discovered_new = discover()
        check_diff(discovered, discovered_new)

        discovered = discovered_new

        logging.info(f"Checking serial")