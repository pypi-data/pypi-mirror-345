"""
Image threshold
"""

import os
import sys

import numpy
import scipy.ndimage

import senchar
import senchar.utils
from senchar.image import Image
import senchar.plot


def threshold_image(filename="test.fits"):
    filename = senchar.db.parameters.get_local_par(
        "threshold_image", "filename", "prompt", "Enter image filename", filename
    )
    if filename == ".":
        reply = senchar.utils.file_browser("", [("image files", ("*.fits"))])
        filename = reply[0]
    if not os.path.isabs(filename):
        filename = senchar.utils.make_image_filename(filename)

    # **************************************************************
    # Threshold data
    # **************************************************************
    im = Image(filename)
    im.assemble(1)
    data = im.buffer
    # halfwidth = 3  # half width in pixels of an event

    # cross structure element
    el = scipy.ndimage.generate_binary_structure(2, 1)
    el = el.astype(numpy.int)

    threshold = data.mean() + 3 * data.std()
    # labels, num = scipy.ndimage.label(data > threshold, numpy.ones((3,3)))
    labels, num = scipy.ndimage.label(data > threshold, el)
    centers = scipy.ndimage.center_of_mass(data, labels, list(range(1, num + 1)))

    x = numpy.array(centers)[:, 0]
    y = numpy.array(centers)[:, 1]

    # r = numpy.sqrt((x-512)**2+(y-512)**2)
    # senchar.plot.plt.hist(r, bins=50)

    xint = x.astype(int)
    yint = y.astype(int)
    values = data[xint, yint]

    bins = int(threshold * 1.2 - threshold * 0.95)
    senchar.plot.plt.hist(values, bins=bins)
    senchar.plot.plt.xlim(threshold * 0.95, threshold * 1.2)
    senchar.plot.plt.show()

    # write and display new image
    im.write_file("filtered.fits", 6)
    senchar.db.tools["display"].display("filtered")

    senchar.plot.plt.show()

    return


if __name__ == "__main__":
    args = sys.argv[1:]
    threshold_image(*args)
