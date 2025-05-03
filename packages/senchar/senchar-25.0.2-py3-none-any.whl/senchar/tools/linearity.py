import glob
import os
import shutil

import numpy

import senchar
import senchar.utils
import senchar.fits
import senchar.plot
from senchar.tools.basetool import Tool


class Linearity(Tool):
    """
    Linearity acquisition and analysis.
    Fit is normally 10% to 90% of estimated saturation.
    Mean residual is mean of absolute residuals in fitted range.
    """

    def __init__(self):
        super().__init__("linearity")

        self.exposure_type = "flat"

        self.number_images_acquire = -1  # number of images to acquire
        self.max_exposure = -1

        self.exposure_times = []  # list of exposure times
        self.exposure_levels = []  # listy of exposure levels [electrons/pixel]

        self.mean_gain = 1.0  # mean system gain e/DN

        self.large_font = 18
        self.small_font = 14
        self.roi = []
        self.rootname = "linearity."

        self.wavelength = -1  # wavelength of acquisition

        self.use_ptc_data = 0  # skips every other image file

        self.overscan_correct = 0  # flag for overscan_correct
        self.zero_correct = 1  # flag to use debiased residuals

        self.fullwell_estimate = 2**16  # estimate of saturation in DN
        self.fit_min_percent = (
            0.10  # percentage of estimated full well for linearity fit
        )
        self.fit_max_percent = 0.90
        self.fit_min_dn = -1  # calculated fit min in DN
        self.fit_max_dn = -1
        self.fit_all_data = 1

        self.fit_order = 3
        """fit order for overscan correction"""

        self.max_allowed_linearity = -1  # max residual for linearity
        self.plot_specifications = 1  # True to plot max_allowed_linearity
        self.use_weights = 1

        self.poly_coeffs = []  # slope and intercept for each channel fit

        self.y_fits = []
        self.residuals = []
        self.mean_residuals = numpy.array([])

        self.plot_fit = 1
        self.plot_residuals = 1
        self.plot_limits = []  # linearity plot limits in %

        self.bad_chans = []  # list of bad channels to ignore

        self.data_file = "linearity.txt"
        self.report_file = "linearity"
        self.linearity_plot = "linearity.png"

        self.max_residual = 0.0

    def analyze(self):
        """
        Analyze a series of flats which have already been taken for linearity.
        """

        senchar.log("Analyzing linearity sequence")

        subfolder = "analysis"
        startingfolder = senchar.utils.curdir()

        if self.use_ptc_data:
            rootname = "ptc."
        else:
            rootname = self.rootname

        if self.overscan_correct or self.zero_correct:
            # create analysis subfolder
            startingfolder, subfolder = senchar.utils.make_file_folder(subfolder)

            # copy all image files to analysis folder
            senchar.log("Making copy of image files for analysis")
            for filename in glob.glob(os.path.join(startingfolder, "*.fits")):
                shutil.copy(filename, subfolder)

            senchar.utils.curdir(
                subfolder
            )  # move for analysis folder - assume it already exists

        else:
            pass

        currentfolder = senchar.utils.curdir()

        _, StartingSequence = senchar.utils.find_file_in_sequence(rootname)

        # Overscan correct all images
        SequenceNumber = StartingSequence
        if self.overscan_correct:
            nextfile = (
                os.path.join(currentfolder, rootname + "%04d" % SequenceNumber)
                + ".fits"
            )
            loop = 0
            filelist = []
            senchar.log("Overscan correct images")
            while os.path.exists(nextfile):
                filelist.append(nextfile)

                # Overscan correct each image
                senchar.log("Overscan correct image: %s" % os.path.basename(nextfile))
                senchar.fits.colbias(nextfile, fit_order=self.fit_order)

                SequenceNumber = SequenceNumber + 1
                nextfile = (
                    os.path.join(currentfolder, rootname + "%04d" % SequenceNumber)
                    + ".fits"
                )
                loop += 1

        # "debias" correct with residuals after colbias
        SequenceNumber = StartingSequence
        if self.zero_correct:
            if self.overscan_correct:
                debiased = senchar.db.tools["bias"].debiased_filename
            else:
                debiased = senchar.db.tools["bias"].superbias_filename
            biassub = "biassub.fits"

            nextfile = (
                os.path.join(currentfolder, rootname + "%04d" % SequenceNumber)
                + ".fits"
            )
            loop = 0
            while os.path.exists(nextfile):
                senchar.fits.sub(nextfile, debiased, biassub)
                os.remove(nextfile)
                os.rename(biassub, nextfile)

                SequenceNumber = SequenceNumber + 1
                nextfile = (
                    os.path.join(currentfolder, rootname + "%04d" % SequenceNumber)
                    + ".fits"
                )
                loop += 1

        self.roi = senchar.utils.get_image_roi()

        zerofilename = rootname + "%04d" % StartingSequence
        zerofilename = senchar.utils.make_image_filename(zerofilename)
        nextfile = zerofilename

        self.NumExt, self.first_ext, self.last_ext = senchar.fits.get_extensions(
            zerofilename
        )

        # read data from image files
        self.exptimes = []  # list of exposure times
        self.means = []  # list of list of means - [ExpTime][Channel] CORRECT!!!
        SequenceNumber = StartingSequence + 1
        while os.path.exists(nextfile):
            flatfilename = rootname + "%04d" % SequenceNumber
            flatfilename = senchar.utils.make_image_filename(flatfilename)
            # flatfilename=os.path.join(currentfolder,flatfilename)+'.fits'

            exptime = float(senchar.fits.get_keyword(flatfilename, "EXPTIME"))

            self.exptimes.append(exptime)
            fmean = senchar.fits.mean(flatfilename, self.roi[0])
            mean = []
            for ext in range(self.first_ext, self.last_ext):
                chan = ext - 1
                x = fmean[chan]
                mean.append(x)
            self.means.append(mean)  # list of all extensions for each exposure time

            SequenceNumber = SequenceNumber + 1
            if self.use_ptc_data:
                SequenceNumber = SequenceNumber + 1
            nextfile = (
                os.path.join(currentfolder, rootname + "%04d" % SequenceNumber)
                + ".fits"
            )

        # find fit limits for linearity
        self.fit_min_dn = self.fit_min_percent * self.fullwell_estimate
        self.fit_max_dn = self.fit_max_percent * self.fullwell_estimate
        if self.fit_all_data:
            minfit = 0
            maxfit = len(self.means) - 1
        else:
            for ext in range(self.first_ext, self.last_ext):
                chan = ext - 1
                if chan == -1:
                    chan = 0
                minfit = minfit1 = 0
                maxfit = maxfit1 = len(self.means) - 1
                m1 = self.means[minfit][chan]
                m2 = self.means[maxfit][chan]
                if chan in self.bad_chans:
                    continue
                if self.fit_min_dn > 0:
                    for x, m in enumerate(self.means):
                        if m[chan] > self.fit_min_dn:
                            minfit1 = x
                            m1 = m[chan]
                            break
                if self.fit_max_dn > 0:
                    for x, m in enumerate(self.means):
                        if m[chan] > self.fit_max_dn:
                            maxfit1 = x  # was x+1
                            m2 = m[chan - 1]  # was chan
                            break
                # senchar.log(minfit1,maxfit1,m1,m2)
                maxfit1 = min(maxfit1, len(self.means) - 1)
                if minfit1 > minfit:
                    minfit = minfit1
                if maxfit1 < maxfit:
                    maxfit = maxfit1
                senchar.log(
                    f"Fit limits for chan {chan} are: {m1:.0f}:{m2:.0f} DN ({self.exptimes[minfit1]:.1f}:{self.exptimes[maxfit1]:.1f} secs)"
                )

        # find residuals for linearity (first and last point)
        self._fit_linearity(minfit, maxfit)  # residuals[chan][exp]

        # make final grade
        """
        maxdev=0.0
        for ext in range(self.first_ext,self.last_ext):
            chan=ext-1
            if chan in self.bad_chans:
                continue
            for i,r in enumerate(self.residuals[chan]):
                if i<minfit or i> maxfit:
                    continue
                if abs(r)>maxdev:
                    maxdev=abs(r)
        self.max_residual=maxdev
        """
        senchar.log(
            f"Largest non-linearity residual is {100. * self.max_residual:0.1f}%"
        )

        # calculate mean linearity
        for ext in range(self.first_ext, self.last_ext):
            # for ext in range(0, self.last_ext - 1):
            ext = ext - 1
            self.mean_residuals = numpy.array(
                [abs(x) for x in self.residuals[ext][minfit:maxfit]]
            ).mean()

        if self.max_allowed_linearity != -1:
            if self.max_residual < self.max_allowed_linearity:
                self.grade = "PASS"
            else:
                self.grade = "FAIL"
            senchar.log(f"Grade = {self.grade}")

        if not self.grade_sensor or self.max_allowed_linearity == -1:
            self.grade = "UNDEFINED"

        # plot
        self.plot(minfit, maxfit, minfit, maxfit)

        # define dataset
        self.dataset = {
            "data_file": self.data_file,
            "NumExt": self.NumExt,
            "max_residual": self.max_residual,
            "fit_min": self.fit_min_dn,
            "fit_max": self.fit_max_dn,
            "poly_coeffs": numpy.array(self.poly_coeffs).tolist(),
            "exptimes": self.exptimes,
            "means": numpy.array(self.means).tolist(),
            "residuals": numpy.array(self.residuals).tolist(),
            "mean_residuals": self.mean_residuals.tolist(),
        }
        if self.max_allowed_linearity != -1:
            self.dataset["grade"] = (self.grade,)
            self.dataset["max_allowed_linearity"] = self.max_allowed_linearity

        # set absolute filenames
        self.linearity_plot = os.path.abspath(self.linearity_plot)

        # write data
        self.write_datafile()
        if self.create_reports:
            self.report()

        # copy data files
        files = [
            "linearity.txt",
            "linearity.md",
            "linearity.pdf",
            "linearity.png",
        ]
        for f in files:
            shutil.copy(f, startingfolder)

        self.is_valid = True

        return

    def _fit_linearity(self, fit_min=-1, fit_max=-1):
        """
        Calculate residuals from linearity data.
        """

        if fit_min == -1:
            fit_min = 0

        xdata = self.exptimes
        num_points = len(xdata)

        if fit_max == -1:
            fit_max = num_points

        # make least squares lineary fit through fit_min to fit_max points
        exptimes = xdata[fit_min:fit_max]

        yfits = []
        polys = []
        for ext in range(self.first_ext, self.last_ext):  # extensions
            chan = ext - 1  # now an index into array, not ext number
            ydata = []
            for i in range(
                fit_min, fit_max
            ):  # means list of extensions per each exp times
                means = self.means[i]
                ydata.append(means[chan])  # ydata is list of means for each exension

            # generate line y values
            if self.use_weights:
                weights = 1.0 / numpy.array(ydata)  # 1./variance
                try:
                    polycoeffs = numpy.polyfit(
                        exptimes, ydata, 1, w=weights
                    )  # [slope,intercept]
                except Exception:
                    polycoeffs = numpy.polyfit(exptimes, ydata, 1, w=weights)
            else:
                polycoeffs = numpy.polyfit(exptimes, ydata, 1)  # [slope,intercept]
            polys.append(list(polycoeffs))  # to list for JSON
            yfit = numpy.polyval(polycoeffs, xdata)  # all data, not xxdata

            yfits.append(yfit)  # yfits[ext][ExpTime]
        self.poly_coeffs = polys
        self.y_fits = yfits

        # calculate residuals for all points
        residuals = []
        for ext in range(self.first_ext, self.last_ext):  # extensions
            chan = ext - 1
            r = []
            for i in range(num_points):  # exp times
                r1 = self.means[i][chan] - yfits[chan][i]  # count difference
                r1 = r1 / yfits[chan][i]  # residual
                r.append(r1)
            residuals.append(r)  # residuals[ext][ExpTime]
        self.residuals = residuals

        # find max_residual
        maxdev = 0.0
        for ext in range(self.first_ext, self.last_ext):
            chan = ext - 1
            if chan in self.bad_chans:
                continue
            for i, r in enumerate(self.residuals[chan]):
                if i < fit_min or i > fit_max:
                    continue
                if abs(r) > maxdev:
                    maxdev = abs(r)
        self.max_residual = maxdev

        return

    def plot(self, MinPoint=0, MaxPoint=-1, MinSpec=-1, MaxSpec=-1):
        """
        Plot linearity and residuals curve(s).
        Min and Max Points are limits for plot (as point numbers).
        Min and Max Spec are x-limits to plot specifications ( as point numbers).

        """

        plotstyle = senchar.plot.style_dot

        fig = senchar.plot.plt.figure()
        fignum = fig.number
        senchar.plot.move_window(fignum)

        # ax1 is linearity
        if self.plot_residuals:
            linplotnum = 211
        else:
            linplotnum = 111
        ax1 = senchar.plot.plt.subplot(linplotnum)
        s = "Linearity"
        senchar.plot.plt.title(s, fontsize=self.large_font)
        senchar.plot.plt.ylabel("Mean [DN]", fontsize=self.small_font)

        # ax2 is residuals
        if self.plot_residuals:
            ax2 = senchar.plot.plt.subplot(212)
            senchar.plot.plt.subplots_adjust(left=0.20, hspace=0.6)
            s = "Linearity Residuals"
            senchar.plot.plt.title(s, fontsize=self.large_font)

        nps = len(plotstyle)

        for chan, _ in enumerate(range(self.first_ext, self.last_ext)):
            if chan in self.bad_chans:
                continue

            # plot linearity
            # senchar.plot.plt.subplot(linplotnum)
            m = []
            for means in self.means:  # exp times
                m.append(means[chan])
            ax1.plot(
                self.exptimes[MinPoint : MaxPoint + 1], m[MinPoint : MaxPoint + 1], "k+"
            )
            senchar.plot.plt.xlabel("Exposure Time [secs]", fontsize=self.small_font)
            # senchar.plot.plt.ylim(0)
            ax1.grid(1)

            # plot fit
            if self.plot_fit:
                ax1.plot(
                    self.exptimes[MinPoint : MaxPoint + 1],
                    self.y_fits[chan][MinPoint : MaxPoint + 1],
                    "r-",
                )

            # plot residuals
            if self.plot_residuals:
                # senchar.plot.plt.subplot(212)
                residuals = self.residuals[chan]
                ax2.plot(
                    self.exptimes[MinPoint : MaxPoint + 1],
                    100.0 * numpy.array(residuals[MinPoint : MaxPoint + 1]),
                    plotstyle[chan % nps],
                )
                senchar.plot.plt.xlabel(
                    "Exposure Time [secs]", fontsize=self.small_font
                )
                senchar.plot.plt.ylabel("Residual [%]", fontsize=self.small_font)
                if self.plot_limits != []:
                    senchar.plot.plt.ylim(self.plot_limits[0], self.plot_limits[1])
                ax2.grid(1)

        # plot specs (one time) on residuals axis
        if self.plot_specifications:
            upper = 100.0 * self.max_allowed_linearity
            lower = -100.0 * self.max_allowed_linearity
            if MinSpec != -1:
                left = self.exptimes[MinSpec]
            else:
                left = self.exptimes[MinPoint]
            if MaxSpec != -1:
                right = self.exptimes[MaxSpec]
            else:
                right = self.exptimes[MaxPoint + 1]
            if self.plot_residuals:
                ax2.plot([left, right], [upper, upper], "b--", linewidth=0.7)
                ax2.plot([left, right], [lower, lower], "b--", linewidth=0.7)

        # show and save plot
        senchar.plot.plt.show()
        senchar.plot.save_figure(fignum, self.linearity_plot)

        return

    def report(self):
        """
        Write report file.
        """

        lines = ["# Linearity Analysis"]

        lines.append(f"Max residual value [%]:   {100. * self.max_residual:0.1f}  ")
        if self.grade != "UNDEFINED":
            lines.append(
                f"Max allowed residual [%]: {100.0 * self.max_allowed_linearity:0.1f}  "
            )
        lines.append(f"Minimum fit limit [DN]: {self.fit_min_dn}  ")
        lines.append(f"Maximum fit limit [DN]: {self.fit_max_dn}  ")
        lines.append(f"Mean residuals [%]: {100. * self.mean_residuals:.1f}  ")
        if self.grade != "UNDEFINED":
            s = f"Linearity grade = {self.grade}  "
            lines.append(s)

        lines.append(
            f"![Linearity and residuals Plot]({os.path.abspath(self.linearity_plot)})  "
        )
        lines.append("*Linearity and residuals Plot.*  ")

        # Make report files
        self.write_report(self.report_file, lines)

        return
