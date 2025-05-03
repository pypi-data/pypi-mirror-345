import os
import shutil
import time

import numpy

import senchar
import senchar.utils
import senchar.fits
from senchar.tools.basetool import Tool


class DetCal(Tool):
    """
    Detector calibration routines to:
     - find and set video offsets
     - find exposure levels in DN and electrons at specified wavelengths
     - find system gains
     - read diode flux calibration data

    Fluxes are reported as per unbinned pixel even if taken binned.
    """

    def __init__(self):
        super().__init__("detcal")

        self.mean_count_goal = 5000
        self.zero_image = "test.fits"
        self.data_file = "detcal.txt"

        self.exposure_type = "flat"
        self.overwrite = 0  # True to overwrite old data
        self.wavelength_delay = 2  # seconds to delay after changing wavelengths
        self.zero_mean = []
        self.system_gain = []

        self.range_factor = 2.0  # allowed range factor for meeting mean goal

        self.exposures = {}  # dictionaries of {wavelength:initial guess et}
        self.mean_counts = {}  # dictionaries of {wavelength:Counts/Sec}
        self.mean_electrons = {}  # dictionaries of {wavelength:Electrons/Sec}

    def calibrate(self):
        """
        Take images at each wavelength to get count levels.
        Use gain data to find offsets and gain.
        If no wavelengths are specified, only calibrate current wavelength
        """

        senchar.log("Running detector calibration sequence")

        # define dataset
        self.dataset = {
            "data_file": self.data_file,
            "wavelengths": wavelengths,
            "mean_electrons": self.mean_electrons,
            "mean_counts": self.mean_counts,
            "system_gain": self.system_gain,
        }

        # write data file
        senchar.utils.curdir(startingfolder)
        self.write_datafile()

        self.is_valid = True

        # finish
        senchar.utils.restore_imagepars(impars)
        senchar.utils.curdir(startingfolder)
        senchar.log("detector calibration sequence finished")

        return

    def read_datafile(self, filename="default"):
        """
        Read data file and set object as valid.
        """

        super().read_datafile(filename)

        # convert types
        self.mean_counts = {int(k): v for k, v in self.mean_counts.items()}
        self.mean_electrons = {int(k): v for k, v in self.mean_electrons.items()}

        return
