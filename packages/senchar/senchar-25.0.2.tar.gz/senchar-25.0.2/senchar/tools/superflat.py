import glob
import os
import shutil

import numpy

import senchar
import senchar.utils
import senchar.fits
import senchar.image
import senchar.plot
import senchar.exceptions
from senchar.tools.basetool import Tool


class Superflat(Tool):
    """
    Flat field image acquisition and analysis.
    """

    def __init__(self):
        super().__init__("superflat")

        # acquire
        self.exposure_type = "flat"
        self.use_exposure_levels = 1
        self.exposure_level = 30000  # exposure level in DN
        self.exposure_time = 1.0  # exposure time if no exposure_level
        self.wavelength = 500.0  # wavelength for images
        self.number_images_acquire = 3  # number of images

        # analyze
        self.masked_image = 0
        self.combination_type = "median"
        self.overscan_correct = 1  # flag to overscan correct images
        self.zero_correct = 0  # flag to correct with bias residuals
        self.superflat_filename = "superflat.fits"  # filename of superflat image
        self.scaled_superflat_filename = (
            "superflatscaled.fits"  # filename of gain corrected fits image
        )
        self.superflat_image_plot = "superflatimage.png"
        self.system_gain = []
        self.grade = "UNDEFINED"
        self.dark_rejected_pixels = 0
        self.dark_pixel_reject = 0.5  # reject pixels below this fraction of mean
        self.allowable_dark_pixels = -1

        self.data_file = "darkdefects.txt"
        self.darkdefects_datafile = "darkdefects.txt"
        self.darkdefectsreport_file = "darkdefects"
        self.darkpixel_rejectionmask = "darkpixel_rejectionmask"

        self.report_include_plots = 1

        self.fit_order = 3
        """fit order for overscan correction"""

    def analyze(self):
        """
        Analyze an existing SuperFlat image sequence for LSST.
        """

        senchar.log("Analyzing superflat sequence")

        rootname = "superflat."
        self.superflat_filename = "superflat.fits"  # filename of superflat image
        self.scaled_superflat_filename = "superflatscaled.fits"  # gain corrected image

        # create analysis subfolder
        startingfolder, subfolder = senchar.utils.make_file_folder("analysis")

        # copy all image files to analysis folder
        senchar.log("Making copy of image files for analysis")
        for filename in glob.glob(os.path.join(startingfolder, "*.fits")):
            shutil.copy(filename, subfolder)

        senchar.utils.curdir(subfolder)  # move to analysis folder

        _, StartingSequence = senchar.utils.find_file_in_sequence(rootname)
        SequenceNumber = StartingSequence

        # start analyzing sequence
        nextfile = os.path.join(subfolder, rootname + "%04d" % SequenceNumber) + ".fits"
        filelist = []
        while os.path.exists(nextfile):
            senchar.log(f"Processing {os.path.basename(nextfile)}")
            filelist.append(nextfile)

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

            SequenceNumber = SequenceNumber + 1
            nextfile = (
                os.path.join(subfolder, rootname + "%04d" % SequenceNumber) + ".fits"
            )

        # median combine all images
        senchar.log(f"Combining superflat images ({self.combination_type})")
        senchar.fits.combine(
            filelist, self.superflat_filename, self.combination_type, overscan_correct=0
        )

        # make superflat image scaled by gain
        if senchar.db.tools["gain"].is_valid:
            self.system_gain = senchar.db.tools["gain"].system_gain
        else:
            senchar.log("WARNING: no gain values found for scaling")
        self.superflat_image = senchar.image.Image(self.superflat_filename)
        if self.overscan_correct:
            zmean = None
        else:
            zmean = senchar.db.tools["gain"].zero_mean
        self.superflat_image.set_scaling(self.system_gain, zmean)
        self.superflat_image.assemble(1)

        # plot superflat image
        fig = senchar.plot.plt.figure()
        fignum = fig.number
        senchar.plot.move_window(fignum)
        senchar.plot.plot_image(self.superflat_image)
        senchar.plot.plt.title("Superflat Combined Image")
        senchar.plot.plt.show()
        senchar.plot.save_figure(fignum, self.superflat_image_plot)

        # save scaled superflat image
        self.superflat_image.overwrite = 1
        self.superflat_image.save_data_format = -32  # could be >16 bits with scaling
        self.superflat_image.write_file(self.scaled_superflat_filename, 6)

        # copy superflat and plot to starting folder
        if startingfolder != subfolder:
            shutil.copy(self.superflat_filename, startingfolder)
            shutil.copy(self.scaled_superflat_filename, startingfolder)
            shutil.copy(self.superflat_image_plot, startingfolder)
            self.superflat_filename = os.path.join(
                startingfolder, self.superflat_filename
            )
            self.scaled_superflat_filename = os.path.join(
                startingfolder, self.scaled_superflat_filename
            )

        # analyze defects
        self.analyze_dark_defects(startingfolder)

        # finish
        senchar.utils.curdir(startingfolder)
        return

    def analyze_dark_defects(self, startingfolder):
        """
        Analyze dark defects in superflat image.
        """

        senchar.log("Analyzing superflat image for dark defects")

        self.grade = "UNDEFINED"
        self.dark_rejected_pixels = 0

        # create masked array
        self.masked_image = numpy.ma.array(self.superflat_image.buffer, mask=False)
        defects = senchar.db.tools["defects"]
        defects.mask_edges(self.masked_image)

        # get total non-masked pixels (not including masked edges)
        self.totalpixels = numpy.ma.count(self.masked_image)

        # calculate stats
        mean = numpy.ma.mean(self.masked_image)
        darklimit = mean * self.dark_pixel_reject
        s = f"Rejecting pixels below {darklimit:.0f} DN ({self.dark_pixel_reject:0.03f} of mean)"
        senchar.log(s)

        self.masked_image = numpy.ma.masked_where(
            self.masked_image < darklimit,
            self.masked_image,
            copy=False,
        )
        self.dark_rejected_pixels = (
            numpy.ma.count_masked(self.masked_image) - defects.number_edgemasked
        )

        senchar.log(
            f"Dark pixels rejected: {self.dark_rejected_pixels}/{self.totalpixels}: {((float(self.dark_rejected_pixels) / self.totalpixels) * 100.0):0.02f}%"
        )

        if self.grade_sensor:
            if self.allowable_dark_pixels != -1:
                if self.dark_rejected_pixels >= self.allowable_dark_pixels:
                    self.grade = "FAIL"
                else:
                    self.grade = "PASS"
                s = f"Grade = {self.grade}"
                senchar.log(s)

        # save dark mask
        fig = senchar.plot.plt.figure()
        fignum = fig.number
        senchar.plot.move_window(fignum)
        senchar.plot.plt.title("Dark Pixel Rejection Mask")

        self.dark_mask = numpy.ma.getmaskarray(self.masked_image).astype("uint8")
        implot = senchar.plot.plt.imshow(self.dark_mask)
        implot.set_cmap("gray")
        senchar.plot.plt.show()
        senchar.plot.save_figure(fignum, self.darkpixel_rejectionmask)  # png file

        # write mask as FITS
        maskfile = senchar.image.Image(self.superflat_filename)
        maskfile.hdulist[0].header["OBJECT"] = "dark pixel mask"
        maskfile.assemble(1)  # for parameters
        maskfile.buffer = self.dark_mask
        maskfile.save_data_format = 8
        maskfile.overwrite = 1
        maskfile.write_file(f"{self.darkpixel_rejectionmask}.fits", 6)

        # copy data files to initial folder
        try:
            shutil.copy(f"{self.darkpixel_rejectionmask}.png", startingfolder)
            shutil.copy(f"{self.darkpixel_rejectionmask}.fits", startingfolder)
        except Exception:
            pass

        # write output files
        senchar.utils.curdir(startingfolder)
        if self.create_reports:
            self.make_dark_defects_report()

        # define dataset
        self.dataset = {
            "darkdefects_datafile": self.darkdefects_datafile,
            "allowable_dark_pixels": self.allowable_dark_pixels,
            "dark_pixel_reject": float(self.dark_pixel_reject),
            "dark_rejected_pixels": float(self.dark_rejected_pixels),
            "data_file": self.data_file,
            "grade": self.grade,
        }

        # write output files
        self.write_datafile()

        return

    def make_dark_defects_report(self):
        """
        Write dark defects report file.
        """

        lines = ["# Superflat/Dark Defects Analysis"]

        lines.append(
            f"Rejecting dark pixels below {self.dark_pixel_reject:.03f} mean  "
        )
        lines.append(f"Number of dark rejected: {int(self.dark_rejected_pixels)}  ")
        if self.allowable_dark_pixels != -1:
            lines.append(f"Allowable bad pixels: {int(self.allowable_dark_pixels)}  ")
            lines.append(f"Grade: {self.grade}  ")

        # add plots
        if self.report_include_plots:
            plotfile = os.path.abspath(self.superflat_image_plot)
            maskfile = os.path.abspath(f"{self.darkpixel_rejectionmask}.png  ")
            lines.append(f"![Superflat image]({plotfile})  ")
            lines.append("*Superflat image.*  ")

            lines.append(f"![Dark pixel rejection mask]({maskfile})  ")
            lines.append("*Dark pixel rejection mask.*  ")

        # Make report files
        self.write_report(self.darkdefectsreport_file, lines)

        return
