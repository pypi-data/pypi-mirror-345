import math
import os
import shutil

import numpy
from astropy.io import fits as pyfits

import senchar
import senchar.utils
import senchar.fits
import senchar.utils
from senchar.tools.basetool import Tool


class Gain(Tool):
    """
    Acquire and analyze gain (PTC point) data.
    """

    def __init__(self):
        super().__init__("gain")

        self.exposure_type = "flat"
        self.exposure_time = -1
        self.exposure_level = -1  # exposure_level in electrons/pixel, -1 do not used
        self.number_pairs = 1
        self.overwrite = 0
        self.wavelength = -1  # -1 do not change wavelength
        self.video_processor_gain = []  # uV/DN for each channel
        self.system_noise_correction = []  # camera noise (no sensor) in DN

        self.include_dark_images = 0  # include dark images in acquire & analysis
        self.dark_frame = None

        self.clear_arrray = 0

        self.readnoise_spec = -1  # read noise spec (max) in electrons

        self.data_file = "gain.txt"
        self.report_file = "gain"

        self.imagefolder = ""
        self.image_zero = ""
        self.image_flat1 = ""
        self.image_flat2 = ""

        # outputs
        self.system_gain = []
        self.noise = []
        self.mean = []
        self.sdev = []
        self.zero_mean = []
        self.sensitivity = []

    def find(self):
        """
        Acquire and Analyze a PTC point for find gain, noise, scale, and offset.
        Does not create a report during analysis.
        """

        createreport = self.create_reports
        self.create_reports = 0

        self.acquire()

        cd = senchar.utils.curdir()
        senchar.utils.curdir(self.imagefolder)

        self.analyze()

        self.create_reports = createreport

        senchar.utils.curdir(cd)

        return

    def analyze(self):
        """
        Analyze a bias image and two flat field images to generate a PTC point.
        """

        senchar.log("Analyzing gain sequence")

        rootname = "ptc."

        # bias image
        _, StartingSequence = senchar.utils.find_file_in_sequence(rootname)
        zerofilename = rootname + f"{StartingSequence:04d}"
        zerofilename = senchar.utils.make_image_filename(zerofilename)
        SequenceNumber = StartingSequence

        NumExt, _, _ = senchar.fits.get_extensions(zerofilename)
        NumExt = max(1, NumExt)

        # get ROI
        self.roi = senchar.utils.get_image_roi()

        # these will be mean values if more than one sequence is analyzed
        self.system_gain = [0] * NumExt
        self.noise = [0] * NumExt
        self.mean = [0] * NumExt
        self.sdev = [0] * NumExt
        self.zero_mean = [0] * NumExt
        self.sensitivity = [0] * NumExt

        loop = 0
        while os.path.exists(zerofilename):
            loop += 1

            SequenceNumber += 1

            if self.include_dark_images:
                darkfilename = rootname + f"{SequenceNumber:04d}"
                darkfilename = darkfilename + ".fits"
                SequenceNumber += 1
            else:
                darkfilename = None

            flat1filename = rootname + f"{SequenceNumber:04d}"
            flat1filename = senchar.utils.make_image_filename(flat1filename)
            SequenceNumber += 1
            flat2filename = rootname + f"{SequenceNumber:04d}"
            flat2filename = senchar.utils.make_image_filename(flat2filename)

            # ExposureTime = float(senchar.fits.get_keyword(flat1filename, "EXPTIME"))

            gain, noise, mean, sdev = self.measure_gain(
                zerofilename, flat1filename, flat2filename, darkfilename
            )

            # correct readnoise
            if self.system_noise_correction != []:
                for chan in range(NumExt):
                    rn = math.sqrt(
                        noise[chan] ** 2
                        - gain[chan] * self.system_noise_correction[chan] ** 2
                    )
                    noise[chan] = rn

            self.system_gain = [a + b for a, b in zip(self.system_gain, gain)]
            self.noise = [a + b for a, b in zip(self.noise, noise)]
            self.mean = [a + b for a, b in zip(self.system_gain, mean)]
            self.sdev = [a + b for a, b in zip(self.sdev, sdev)]

            # get zero mean for Offset
            zeromean = senchar.fits.mean(zerofilename, self.roi[1])
            self.zero_mean = [a + b for a, b in zip(self.zero_mean, zeromean)]

            senchar.log("Channel system_gain[e/DN] Noise[e]")
            for i in range(len(self.system_gain)):
                senchar.log(
                    f"{i:02d}      {gain[i]:0.02f}             {noise[i]:0.01f}"
                )

            SequenceNumber = SequenceNumber + 1
            zerofilename = rootname + f"{SequenceNumber:04d}"
            zerofilename = senchar.utils.make_image_filename(zerofilename)

        # get means from sums
        self.system_gain = [x / loop for x in self.system_gain]
        self.noise = [x / loop for x in self.noise]
        self.mean = [x / loop for x in self.mean]
        self.sdev = [x / loop for x in self.sdev]
        self.zero_mean = [x / loop for x in self.zero_mean]

        # set grade based on read noise only
        if self.readnoise_spec != -1:
            self.grade = "PASS"
            for rn in self.noise:
                if rn > self.readnoise_spec:
                    self.grade = "FAIL"
                    break

        if self.video_processor_gain != []:
            for chan, gain in enumerate(self.system_gain):
                self.sensitivity[chan] = self.video_processor_gain[chan] / gain

        # define dataset
        self.dataset = {
            "data_file": self.data_file,
            "grade": self.grade,
            "system_noise_correction": [float(x) for x in self.system_noise_correction],
            "system_gain": [float(x) for x in self.system_gain],
            "noise": [float(x) for x in self.noise],
            "mean": [float(x) for x in self.mean],
            "sdev": [float(x) for x in self.sdev],
            "zero_mean": [float(x) for x in self.zero_mean],
            "sensitivity": [float(x) for x in self.sensitivity],
        }

        # write output files
        self.write_datafile()
        if self.create_reports:
            self.report()

        # finish
        self.is_valid = 1

        return

    def measure_gain(self, Zero, Flat1, Flat2, Dark=None):
        """
        Calculate gain and noise from a bias and photon transfer image pair.
        """

        Zero = senchar.utils.make_image_filename(Zero)
        Flat1 = senchar.utils.make_image_filename(Flat1)
        Flat2 = senchar.utils.make_image_filename(Flat2)

        if Dark is not None:
            Dark = senchar.utils.make_image_filename(Dark)

        # extensions are elements 1 -> NumExt
        NumExt, first_ext, last_ext = senchar.fits.get_extensions(Zero)
        if NumExt == 0:
            data_ffci = []
            gain = []
            noise = []
            flat_mean = []
            ffci_sdev = []
            NumExt = 1
        elif NumExt == 1:
            data_ffci = [0]
            gain = [0]
            noise = [0]
            flat_mean = [0]
            ffci_sdev = [0]
        else:
            data_ffci = [0]
            gain = [0]
            noise = [0]
            flat_mean = [0]
            ffci_sdev = [0]

        # get ROI
        self.roi = senchar.utils.get_image_roi()

        # get zero mean and sigma
        zmean = senchar.fits.mean(Zero, self.roi[1])
        zsdev = senchar.fits.sdev(Zero, self.roi[1])

        if self.include_dark_images:
            dmean = senchar.fits.mean(Dark, self.roi[0])

        # get flat mean for each extension
        fmean = senchar.fits.mean(Flat1, self.roi[0])
        for ext in range(first_ext, last_ext):
            if self.include_dark_images:
                flat_mean.append(fmean[ext - 1] - dmean[ext - 1])
            else:
                flat_mean.append(fmean[ext - 1] - zmean[ext - 1])

        # open files
        imf1 = pyfits.open(Flat1)
        imf2 = pyfits.open(Flat2)
        if self.include_dark_images:
            dark1 = pyfits.open(Dark)

        # make ffci data
        #   order is .data[] order, not EXT/IM order
        for ext in range(first_ext, last_ext):
            imf1[ext].data = imf1[ext].data.astype("float32")
            imf2[ext].data = imf2[ext].data.astype("float32")
            if self.include_dark_images:
                dark1[ext].data = dark1[ext].data.astype("float32")
                data_ffci.append(imf1[ext].data - dark1[ext].data)
            else:
                data_ffci.append(imf1[ext].data - imf2[ext].data)

        imf1.close()
        imf2.close()

        # get stats in same ROI of each section
        roi = self.roi[0]
        for ext in range(first_ext, last_ext):
            ffci_sdev.append(
                data_ffci[ext][roi[2] : roi[3], roi[0] : roi[1]].std() / math.sqrt(2.0)
            )
            try:
                g = flat_mean[ext] / (ffci_sdev[ext] ** 2 - zsdev[ext - 1] ** 2)
                if numpy.isnan(g):
                    gain.append(0.0)
                else:
                    gain.append(g)
            except Exception as message:
                senchar.log(message)
                gain.append(0.0)
            noise.append(gain[ext] * zsdev[ext - 1])

        if len(gain) > 1:
            return [
                gain[1:],
                noise[1:],
                flat_mean[1:],
                ffci_sdev[1:],
            ]  # these are all lists
        else:
            return [gain, noise, flat_mean, ffci_sdev]  # these are all lists

    def get_system_gain(self):
        """
        Returns the system gain.
        """

        if self.is_valid:
            if self.system_gain == []:
                self.analyze()
        else:
            self.read_datafile()

        return self.system_gain

    def report(self):
        """
        Make report files.
        """

        lines = ["# Gain Analysis"]

        if self.system_noise_correction == []:
            s = "Read Noise in electrons is not system noise corrected  "
            lines.append(s)
        else:
            s = "Read Noise in electrons is system noise corrected  "
            lines.append(s)
            mean = numpy.array(self.system_noise_correction).mean()
            s = f"Mean system noise correction = {mean:5.01f} DN  "
            lines.append(s)

        if self.grade != "UNDEFINED":
            s = f"Gain grade = {self.grade}  "
            lines.append(s)

        if self.readnoise_spec != -1:
            s = f"Read noise spec = {self.readnoise_spec:5.1f} electrons  "
            lines.append(s)

        lines.append("")
        s = "|**Channel**|**Gain [e/DN]**|**Noise [e]**|**Sens. [uV/e]**|**Bias[DN]**|"
        lines.append(s)
        s = "|:---|:---:|:---:|:---:|:---:|"
        lines.append(s)

        for chan in range(len(self.system_gain)):
            s = f"|{chan:02d}|{self.system_gain[chan]:5.02f}|{self.noise[chan]:5.01f}|{self.sensitivity[chan]:5.02f}|{self.zero_mean[chan]:7.01f}|"
            lines.append(s)

        # Make report files
        self.write_report(self.report_file, lines)

        return

    def fe55_gain(self):
        """
        Set gain.system_gain to senchar.db.tools["fe55"].system_gain values.
        """

        self.system_gain = senchar.db.tools["fe55"].system_gain

        return
