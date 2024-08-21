import sys

from cursor.data import DataDirHandler
from cursor.load.loader import Loader
from cursor.properties import Property

import logging


def load_single_with_color():
    dir = DataDirHandler().recordings()
    single_file = dir / "1698160256.57273_final_color.json"
    ll = Loader()
    ll.load_file(single_file)

    all_paths = ll.all_paths()
    files_with_colors = set()

    for path in all_paths:
        for point in path:
            if point.properties[Property.COLOR]:
                files_with_colors.add(single_file)
                # logging.info(file)
                # logging.info(f"{point}")

    print(files_with_colors)


def check_recordings_for_colored():
    dir = DataDirHandler().recordings()

    all_files = []
    for file in dir.iterdir():
        if file.as_posix().endswith(".json"):
            all_files.append(file.name)

    files_with_colors = set()

    for file in all_files:
        ll = Loader()
        ll.load_file(dir / file)
        all_paths = ll.all_paths()

        for path in all_paths:
            for point in path:
                if point.properties[Property.COLOR]:
                    files_with_colors.add(file)
                    # logging.info(file)
                    # logging.info(f"{point}")

    print(files_with_colors)
    # colored_files = {
    #    "1664202496.255067_bangkok color.json",
    #    "1678563558.003206_5 min auto save.json",
    #    "1688072168.683101_moved to osw.json",
    #    "1681898121.96604_pepe_day3_2.json",
    #    "1677488250.320736_montags.json",
    #    "1664178112.612016_colors better.json",
    #    "1688644077.119991_upwardupwardupward.json",
    #    "1664178785.14013_even better colors.json",
    #    "1690029652.414826_refactoring.json",
    #    "1688483128.248166_ronald kommt zu besuch.json",
    #    "1664388180.973089_back home.json",
    #    "1676293094.665719_random_monday.json",
    #    "1664174605.599717_colors.json",
    #    "1668603147.378996_after a long time.json",
    #    "1689137767.169443_reboot.json",
    #    "1687022310.710539_schwittstation_working.json",
    #    "1680966742.23158_taxes.json",
    #    "1690633874.155586_luminograms new.json",
    #    "1687364854.748665_after_birthday.json",
    #    "1687441424.055778_volt power supply testing.json",
    #    "1681374284.202464_thursday reorganize everdo finally.json",
    #    "1680796458.376814_octet raffle accepting session.json",
    #    "1667479655.359377_day before vernissage.json",
    #    "1665834971.510907_saturday interview writing.json",
    #    "1681132631.295536_octet token minting.json",
    #    "1669985689.52639_studio.json",
    #    "1676454136.777945_random_wednesday.json",
    #    "1681890003.263651_pepe day 3.json",
    #    "1688935894.902238_sleeping in osw.json",
    #    "1664274154.429897_last evening bangkok.json",
    #    "1689464914.167903_holo text working.json",
    # }


if __name__ == "__main__":
    load_single_with_color()

    # check_recordings_for_colored()
    sys.exit(0)

    recordings = DataDirHandler().recordings()
    _loader = Loader(directory=recordings, limit_files=1)
    all_paths = _loader.all_paths()

    for path in all_paths:
        for point in path:
            if point.properties[Property.COLOR]:
                logging.info(f"{point}")
