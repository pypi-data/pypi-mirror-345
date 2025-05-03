"""
Display a sequence of files interactively on ds9
"""

import os
import sys

import senchar
import senchar.utils
from senchar.utils import beep


def display_files():
    # loop through files
    QUIT = 0
    for root, topfolders, filenames in os.walk("."):
        if QUIT:
            break

        for filename in filenames:
            if not filename.endswith(".fits"):
                continue
            beep(2000, 1)
            f = os.path.join(root, filename)
            print(f)

            senchar.db.tools["display"].display(f)
            senchar.db.tools["display"].zoom(0)

            print("Press Enter to continue, s to snap, q to quit")
            key = senchar.utils.check_keyboard(1)

            if key.lower() == "q":
                QUIT = 1
                break

            elif key == "s":
                senchar.db.tools["display"].save_image()

    return


if __name__ == "__main__":
    args = sys.argv[1:]
    display_files(*args)
