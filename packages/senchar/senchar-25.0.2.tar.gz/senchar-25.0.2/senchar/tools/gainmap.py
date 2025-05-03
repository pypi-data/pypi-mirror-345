import math
import os
import shutil

import numpy
from astropy.io import fits as pyfits

import senchar
import senchar.utils
import senchar.fits
import senchar.image
import senchar.utils
import senchar.plot
from senchar.tools.basetool import Tool


class GainMap(Tool):
    """
    Acquire and analyze gain (PTC point) data.
    """

    def __init__(self):
        super().__init__("gainmap")

        self.exposure_type = "flat"
        self.exposure_time = -1
        self.exposure_level = -1  # exposure_level in electrons/pixel, -1 do not used
        self.number_flat_images = 10
        self.number_bias_images = 10
        self.overwrite = 0
        self.wavelength = -1  # -1 do not change wavelength
        self.clear_arrray = 0

        self.data_file = "gainmap.txt"
        self.gainmap_fitsfile = "gainmap.fits"
        self.gainmap_plotfile = "gainmap.png"
        self.report_file = "gainmap"

        # files
        self.imagefolder = ""
        self.flat_filenames = []
        self.bias_filenames = []

        # images
        self.flat_images = []
        self.bias_images = []
        self.flatcube = numpy.array
        self.mean_flatimage = numpy.array
        self.sdev_flatimage = numpy.array
        self.var_flatimage = numpy.array

        self.biascube = numpy.array
        self.mean_biasimage = numpy.array
        self.sdev_biasimage = numpy.array

        self.gainmap_image = numpy.array

        self.image_zero = ""
        self.image_flat1 = ""
        self.image_flat2 = ""

        # outputs
        self.gain_min = 0
        self.gain_max = 0
        self.gain_median = 0

        self.system_gain = []
        self.noise = []
        self.mean = []
        self.sdev = []
        self.zero_mean = []

    def analyze(self):
        """
        Analyze a bias image and multiple flat field images to generate a PTC point at every pixel.
        """

        senchar.log("Analyzing gainmap sequence")

        startingfolder = senchar.utils.curdir()

        # get list of bias images
        rootname = "bias."
        _, starting_sequence = senchar.utils.find_file_in_sequence(rootname)
        sequence_number = starting_sequence
        self.bias_filenames = []
        while True:
            biasfile = (
                os.path.join(startingfolder, rootname + f"{sequence_number:04d}")
                + ".fits"
            )
            if not os.path.exists(biasfile):
                break
            biasfile = senchar.utils.fix_path(biasfile)
            self.bias_filenames.append(biasfile)
            sequence_number += 1

        # get list of all flat images
        rootname = "gainmap."
        _, starting_sequence = senchar.utils.find_file_in_sequence(rootname)
        sequence_number = starting_sequence
        self.flat_filenames = []
        while True:
            flatfile = (
                os.path.join(startingfolder, rootname + f"{sequence_number:04d}")
                + ".fits"
            )
            if not os.path.exists(flatfile):
                break
            flatfile = senchar.utils.fix_path(flatfile)
            self.flat_filenames.append(flatfile)
            sequence_number += 1

        NumExt, _, _ = senchar.fits.get_extensions(self.bias_filenames[0])
        NumExt = max(1, NumExt)

        # these will be mean values if more than one sequence is analyzed
        self.system_gain = [0] * NumExt
        self.noise = [0] * NumExt
        self.mean = [0] * NumExt
        self.sdev = [0] * NumExt
        self.zero_mean = [0] * NumExt

        loop = 0

        # make assembled bias images
        self.bias_images = []
        for frame in self.bias_filenames:
            im = senchar.image.Image(frame)
            im.assemble(1)  # assembled an trim overscan
            self.bias_images.append(im)

        # make assembled flat images
        self.flat_images = []
        for frame in self.flat_filenames:
            im = senchar.image.Image(frame)
            im.assemble(1)  # assembled an trim overscan
            self.flat_images.append(im)

        # stack data and make 2D stats
        self.flatcube = numpy.stack([im.buffer for im in self.flat_images])
        self.mean_flatimage = self.flatcube.mean(axis=0)
        self.sdev_flatimage = self.flatcube.std(axis=0)
        self.var_flatimage = numpy.square(self.sdev_flatimage)

        self.biascube = numpy.stack([im.buffer for im in self.bias_images])
        self.mean_biasimage = self.biascube.mean(axis=0)
        self.sdev_biasimage = self.biascube.std(axis=0)
        self.var_biasimage = numpy.square(self.sdev_biasimage)

        # make gain map
        self.gainmap_image = self.mean_flatimage / (
            self.var_flatimage - self.var_biasimage
        )
        self.gain_mean = self.gainmap_image.mean()
        self.gain_min = self.gainmap_image.min()
        self.gain_max = self.gainmap_image.max()
        self.gain_median = numpy.median(self.gainmap_image)
        self.gain_sdev = self.gainmap_image.std()

        # outputs
        senchar.log(f"Mean gain is {self.gain_mean:0.02f}")
        senchar.log(f"Minimum gain is {self.gain_min:0.02f}")
        senchar.log(f"Maximum gain is {self.gain_max:0.02f}")
        senchar.log(f"Median gain is {self.gain_median:0.02f}")
        senchar.log(f"Gain sdev is {self.gain_sdev:0.02f}")

        senchar.plot.plt.imshow(
            self.gainmap_image,
            cmap="gray",
            origin="lower",
            vmin=self.gain_mean - self.gain_sdev,
            vmax=self.gain_mean + self.gain_sdev,
        )
        senchar.plot.plt.title("Gain Map")
        fignum = senchar.plot.plt.gcf().number
        senchar.plot.save_figure(fignum, self.gainmap_plotfile)
        senchar.plot.move_window(fignum)

        # create gainmap FITS file
        hdul = pyfits.HDUList()
        hdul.append(pyfits.PrimaryHDU())
        hdul.append(pyfits.ImageHDU(data=self.gainmap_image))
        hdul.writeto(self.gainmap_fitsfile, overwrite=True)

        # define dataset
        self.dataset = {
            "data_file": self.data_file,
            "gain_mean": f"{self.gain_mean:0.03f}",
            "gain_min": f"{self.gain_min:0.03f}",
            "gain_max": f"{self.gain_max:0.03f}",
            "gain_median": f"{self.gain_median:0.03f}",
            "gain_sdev": f"{self.gain_sdev:0.03f}",
        }

        # write output files
        self.write_datafile()
        if self.create_reports:
            self.report()

        # finish
        self.is_valid = 1

        return

    def report(self):
        """
        Make report files.
        """

        lines = ["# Gain Map"]

        s = f"Gain mean = {self.gain_mean:0.03f}  "
        lines.append(s)
        s = f"Gain minimum = {self.gain_min:0.03f}  "
        lines.append(s)
        s = f"Gain maximum = {self.gain_max:0.03f}  "
        lines.append(s)
        s = f"Gain median = {self.gain_median:0.03f}  "
        lines.append(s)
        s = f"Gain sdev = {self.gain_sdev:0.03f}  "
        lines.append(s)

        lines.append(f"![Dark Image]({os.path.abspath(self.gainmap_plotfile)})  ")
        lines.append("*Gain Map Image.*")

        # Make report files
        self.write_report(self.report_file, lines)

        return
