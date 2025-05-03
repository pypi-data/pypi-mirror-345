"""
check_bits.py
Adapted from code by Ian McGreer.
"""

import sys

import numpy as np
from astropy.io import fits as fits_io

import senchar
import senchar.utils


def check_bits(filename: str) -> None:
    """
    Prints the fraction of pixels in an image with each bit set.
    Value should be 0.5 except for high order bits.

    Args:
        filename: image filename
    """

    filename = senchar.utils.make_image_filename(filename)
    with fits_io.open(filename) as fitsfile:
        print("%5s  " % "", end="")
        for bit in range(16):
            print(f"bit{bit:02} ", end="")
        print("")
        for ext, hdu in enumerate(fitsfile[1:], start=1):
            print(f"HDU{ext:02}  ", end="")
            data = hdu.data.astype(np.uint16)
            npix = float(data.size)
            for bit in range(16):
                nbit = np.sum((data & (1 << bit)) > 0)
                fbit = nbit / npix
                print(f"{fbit:5.3f} ", end="")
            print("")


if __name__ == "__main__":
    args = sys.argv[1:]
    check_bits(*args)
