"""
PLot a histogram of image to check ADC.
"""

import sys

import numpy

import senchar
from senchar.image import Image
import senchar.plot


def show_histogram(filename: str) -> None:
    """
    Plot a histogram of pixel values.
    Uses assembled images so all HDU's are included together.

    Args:
        filename: iamge filename
    """

    im1 = Image(filename)
    im1.assemble(1)
    data = im1.buffer

    # make histogram
    hist_y, hist_x = numpy.histogram(data, bins="auto")
    centers = (hist_x[:-1] + hist_x[1:]) / 2

    # plot
    fig, ax = senchar.plot.plt.subplots(constrained_layout=False)
    senchar.plot.plt.semilogy([int(x) for x in centers], hist_y)
    xlabel = "Pixel Value"
    ylabel = "Number of Events"
    title = "Image Histogram"
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    senchar.plot.plt.ylim(1)
    ax.grid(True)
    senchar.plot.plt.show()

    return


if __name__ == "__main__":
    args = sys.argv[1:]
    show_histogram(*args)
