import glob
import os
import shutil
import math

import numpy

import senchar
import senchar.utils
import senchar.fits
import senchar.utils
import senchar.image
from senchar.tools.basetool import Tool


class Prnu(Tool):
    """
    Photo-Response Non-Uniformity (PRNU) acquisition and analysis.
    """

    def __init__(self):
        super().__init__("prnu")

        self.exposure_type = "flat"
        self.root_name = "prnu."  # allow for analyzing QE data
        self.allowable_deviation_from_mean = -1  # allowable deviation from mean signal
        self.exposure_levels = {}  # dictionary of {wavelength:exposure times}
        self.mean_count_goal = 0  # use detcal data if > 0
        self.grades = {}  # Pass/Fail grades at each wavelength {wave:grade}

        self.fit_order = 3
        """fit order for overscan correction"""

        self.bias_image_in_sequence = 1  # flag true if first image is a bias image

        self.overscan_correct = 0  # flag to overscan correct images
        self.zero_correct = 0  # flag to correct with bias residuals

        self.roi_prnu = []  # empty to use entire sensor

        # outputs
        self.prnu_file = ""
        self.prnus = {}  # PRNU at each image in sequence {wavelength:PRNU}

        self.data_file = "prnu.txt"
        self.report_file = "prnu"

    def analyze(self, copy_files=0):
        """
        Analyze an existing PRNU image sequence.
        """

        senchar.log("Analyzing PRNU sequence")

        rootname = self.root_name
        self.grade = "UNDEFINED"
        subfolder = "analysis"
        self.images = []

        # analysis subfolder
        startingfolder, subfolder = senchar.utils.make_file_folder(subfolder)
        senchar.log("Making copy of image files for analysis")
        for filename in glob.glob(os.path.join(startingfolder, "*.fits")):
            shutil.copy(filename, subfolder)
        senchar.utils.curdir(subfolder)
        currentfolder = senchar.utils.curdir()
        _, StartingSequence = senchar.utils.find_file_in_sequence(rootname)
        SequenceNumber = StartingSequence

        # bias image (first in sequence)
        zerofilename = rootname + "%04d" % StartingSequence
        zerofilename = os.path.join(currentfolder, zerofilename) + ".fits"
        zerofilename = senchar.utils.make_image_filename(zerofilename)

        if self.bias_image_in_sequence:
            SequenceNumber += 1

        nextfile = os.path.normpath(
            os.path.join(currentfolder, rootname + "%04d" % (SequenceNumber)) + ".fits"
        )

        # get gain values
        if senchar.db.tools["gain"].is_valid:
            self.system_gain = senchar.db.tools["gain"].system_gain
        else:
            senchar.log("WARNING: no gain values found for scaling")
            numext, _, _ = senchar.fits.get_extensions(zerofilename)
            self.system_gain = numext * [1.0]

        # loop over files
        self.grades = {}
        while os.path.exists(nextfile):
            wavelength = senchar.fits.get_keyword(nextfile, "WAVLNGTH")
            wavelength = int(float(wavelength) + 0.5)
            senchar.log("Processing image %s" % os.path.basename(nextfile))

            # colbias
            if self.overscan_correct:
                senchar.fits.colbias(nextfile, fit_order=self.fit_order)

            # "debias" correct with residuals after colbias
            if self.zero_correct:
                debiased = senchar.db.tools["bias"].debiased_filename
                biassub = "biassub.fits"
                senchar.fits.sub(nextfile, debiased, biassub)
                os.remove(nextfile)
                os.rename(biassub, nextfile)

            # scale to electrons by system gain
            prnuimage = senchar.image.Image(nextfile)

            if self.overscan_correct:
                prnuimage.set_scaling(self.system_gain, None)
            else:
                prnuimage.set_scaling(
                    self.system_gain, senchar.db.tools["gain"].zero_mean
                )
            prnuimage.assemble(1)
            prnuimage.save_data_format = -32
            prnuimage.write_file("prnu_%d.fits" % wavelength, 6)

            # create masked array
            self.masked_image = numpy.ma.array(prnuimage.buffer, mask=False)
            defects = senchar.db.tools["defects"]
            defects.mask_defects(self.masked_image)

            # apply defects mask
            self.masked_image = numpy.ma.array(prnuimage.buffer, mask=False)
            defects = senchar.db.tools["defects"]
            defects.mask_edges(self.masked_image)

            # optionally use ROI
            if len(self.roi_prnu) == 0:
                stdev = numpy.ma.std(self.masked_image)
                mean = numpy.ma.mean(self.masked_image)
            else:
                maskedimage = self.masked_image[
                    self.roi_prnu[2] : self.roi_prnu[3],
                    self.roi_prnu[0] : self.roi_prnu[1],
                ]
                stdev = numpy.ma.std(maskedimage)
                mean = numpy.ma.mean(maskedimage)

            # account for signal shot noise
            prnu = math.sqrt(stdev**2 - mean) / mean

            self.prnus[wavelength] = float(prnu)
            if self.allowable_deviation_from_mean != -1:
                if prnu <= self.allowable_deviation_from_mean:
                    GRADE = "PASS"
                else:
                    GRADE = "FAIL"
            else:
                GRADE = "UNDEFINED"

            self.grades[wavelength] = GRADE

            s = "PRNU at %7.1f nm is %5.1f%%, Grade = %s" % (
                wavelength,
                prnu * 100,
                GRADE,
            )
            senchar.log(s)

            SequenceNumber = SequenceNumber + 1
            nextfile = (
                os.path.join(currentfolder, rootname + "%04d" % SequenceNumber)
                + ".fits"
            )

        if "FAIL" in list(self.grades.values()):
            self.grade = "FAIL"
        else:
            self.grade = "PASS"
        s = "Grade = %s" % self.grade

        if not self.grade_sensor:
            self.grade = "UNDEFINED"

        senchar.log(s)

        # define dataset
        self.dataset = {
            "data_file": self.data_file,
            "grade": self.grade,
            "allowable_deviation_from_mean": self.allowable_deviation_from_mean,
            "Prnus": self.prnus,
            "grades": self.grades,
        }

        # write data file
        self.write_datafile()
        if self.create_reports:
            self.report()

        # copy data files
        files = ["prnu.txt", "prnu.md", "prnu.pdf"]
        for f in files:
            shutil.copy(f, startingfolder)

        # write data file
        senchar.utils.curdir(startingfolder)
        self.write_datafile()
        if self.create_reports:
            self.report()

        # finish
        self.is_valid = True
        return

    def report(self):
        """
        Write dark report file.
        """

        lines = ["# PRNU Analysis"]

        if self.allowable_deviation_from_mean != -1:
            if self.grade != "UNDEFINED":
                s = f"PRNU spec= {(self.allowable_deviation_from_mean * 100.0):.1f}%  "
                lines.append(s)
                s = f"PRNU grade = {self.grade}  "
                lines.append(s)

        lines.append("")
        s = "|**Wavelength**|**PRNU [%]**|"
        lines.append(s)
        s = "|:---|:---:|"
        lines.append(s)

        waves = list(self.prnus.keys())
        waves.sort()
        for wave in waves:
            s = f"|{wave:04d}|{(100.0 * self.prnus[wave]):7.01f}|"
            lines.append(s)

        # Make report files
        self.write_report(self.report_file, lines)

        return
