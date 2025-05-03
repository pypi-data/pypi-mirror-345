import math
import os

import numpy
from astropy.io import fits as pyfits

import senchar
import senchar.utils
import senchar.fits
import senchar.plot
from senchar.tools.basetool import Tool


class Ramp(Tool):
    """
    Ramp image acquisition and analysis for fast PTC measurements.
    """

    def __init__(self):
        super().__init__("ramp")

        self.ext_analyze = -1  # extension to analyze if not entire image

        self.exposure_type = "flat"  # not reset as system dependent
        self.ramp_file = "ramp.txt"
        self.point_analysis = 0
        self.fit_min = 0
        self.fit_max = 0
        self.means = []
        self.sdevs = []
        self.gains = []
        self.noises = []
        self.exposure_times = []
        self.num_chans = -1

        self.first_col = -1
        self.last_col = -1

        self.logplot = 1
        self.include_dark_current = 0

    def analyze(self, MaxRow=-1):
        """
        Analyze an exisiting series of ramp images.
        """

        rootname = "ramp."
        self.MaxRow = MaxRow

        _, StartingSequence = senchar.utils.find_file_in_sequence(rootname)
        SequenceNumber = StartingSequence

        CurrentFolder = senchar.utils.curdir()

        # get ROI
        self.roi = senchar.utils.get_image_roi()

        # bias image
        zerofilename = rootname + "%04d" % StartingSequence
        zerofilename = os.path.join(CurrentFolder, zerofilename) + ".fits"
        zerofilename = senchar.utils.make_image_filename(zerofilename)

        # create ramp.txt text file
        self.ramp_file = os.path.join(CurrentFolder, "ramp.txt")
        with open(self.ramp_file, "w") as f:
            s = "#Mean    Sdev     Noise Gain     Ext. ExpTime  filename"
            f.write(s + "\n")

            SequenceNumber = SequenceNumber + 1
            ramp1filename = rootname + "%04d" % SequenceNumber
            ramp1filename = os.path.join(CurrentFolder, ramp1filename) + ".fits"
            SequenceNumber = SequenceNumber + 1
            ramp2filename = rootname + "%04d" % SequenceNumber
            ramp2filename = os.path.join(CurrentFolder, ramp2filename) + ".fits"

            self.gains, self.means, self.sdevs = self.measure(
                zerofilename, ramp1filename, ramp2filename
            )

            self.num_chans = len(self.gains)
            self.num_points = len(self.gains[0])

        # now plot
        if self.create_plots:
            self.plot()

        return

    def measure(self, Zero, Ramp1, Ramp2):
        """
        Calculate ptc data from a bias and two ramp images.
        """

        Ramp1 = senchar.utils.make_image_filename(Ramp1)
        Ramp2 = senchar.utils.make_image_filename(Ramp2)

        # extentions are elements 1 -> NumExt
        NumExt, first_ext, last_ext = senchar.fits.get_extensions(Zero)
        if NumExt == 0:
            data_ffci = []
            data_mean = []
            NumExt = 1
        elif NumExt == 1:
            data_ffci = [0]
            data_mean = [0]
        else:
            data_ffci = [0]
            data_mean = [0]

        # get bias mean and sigma
        zmean = senchar.fits.mean(Zero)
        zsdev = senchar.fits.sdev(Zero)

        # open files
        im1 = pyfits.open(Ramp1)
        im2 = pyfits.open(Ramp2)

        # get image size
        hdr = im1[first_ext].header
        ncols = hdr["NAXIS1"]
        nrows = hdr["NAXIS2"]

        # get mean and ffci data shaped to [ext][rows][cols]
        for ext in range(first_ext, last_ext):
            senchar.log(ext, first_ext, last_ext)
            data_ffci.append(im1[ext].data - im2[ext].data)
            data_ffci[ext] = numpy.reshape(data_ffci[ext], [nrows, ncols])
            data_mean.append(im1[ext].data - zmean[ext - 1])
            data_mean[ext] = numpy.reshape(data_mean[ext], [nrows, ncols])

        # perhaps ignore edges
        if self.first_col == -1:
            self.first_col = 1
        if self.last_col == -1:
            self.last_col = ncols

        if self.MaxRow != -1:
            nrows = self.MaxRow

        # get stats in same ROI of each line
        gains = []
        means = []
        sdevs = []
        for ext in range(first_ext, last_ext):
            gains = []
            means = []
            sdevs = []
            for row in range(nrows):
                roi = [self.first_col - 1, self.last_col, row, row + 1]
                sdev = data_ffci[ext][roi[2] : roi[3]][
                    roi[0] : roi[1]
                ].std() / math.sqrt(2.0)
                fmean = data_mean[ext][roi[2] : roi[3]][roi[0] : roi[1]].mean()
                sdevs.append(sdev)
                means.append(fmean)
                try:
                    g = fmean / (sdev**2 - zsdev[ext - 1] ** 2)
                    if numpy.isnan(g):
                        gains.append(0.0)
                    else:
                        gains.append(g)
                except Exception as message:
                    senchar.log(message)
                    gains.append(0.0)

            gains.append(gains)
            means.append(means)
            sdevs.append(sdevs)

        # finish

        im1.close()
        im2.close()

        return [gains, means, sdevs]

    def plot(self):
        """
        Plot ramp data from ptc.means, ptc.sdevs, ptc.gains.
        This version plots on a log-log scale.
        This version makes one plot with multiple line types and colors (not subplots).
        """

        # single plot
        #    (get subplot pars with figure(1).subplotpars.left, etc.)
        bigfont = 22
        mediumfont = 16
        smallfont = 14
        ptop = 0.85
        pbottom = 0.18
        pleft = 0.12
        pright = 0.95
        wspace = None
        hspace = None
        marksize = 5
        plotstyle = senchar.plot.style_dot

        # setup PTC figure
        f1 = senchar.plot.plt.figure(1)
        f1.clf()  # clear old data
        f1.text(
            0.5,
            0.93,
            r"$\rm{Ramp\ Photon\ Transfer\ Curve}$",
            horizontalalignment="center",
            fontsize=bigfont,
        )
        f1.subplots_adjust(
            left=pleft,
            bottom=pbottom,
            right=pright,
            top=ptop,
            wspace=wspace,
            hspace=hspace,
        )
        fig1 = senchar.plot.plt.subplot(1, 1, 1)
        fig1.xaxis.grid(1, which="both")  # log lines
        fig1.yaxis.grid(1)

        # axes
        senchar.plot.plt.xlabel("Mean Signal [DN]", fontsize=mediumfont)
        senchar.plot.plt.ylabel("Noise [DN]", fontsize=mediumfont)
        ax = senchar.plot.plt.gca()
        for label in ax.yaxis.get_ticklabels():
            label.set_fontsize(smallfont)
        for label in ax.xaxis.get_ticklabels():
            label.set_rotation(45)
            label.set_fontsize(smallfont)

        # setup gain figure
        fig2 = senchar.plot.plt.figure(2)
        fig2.clf()  # clear old data
        fig2.text(
            0.5,
            0.93,
            r"$\rm{Ramp\ System\ Gain}$",
            horizontalalignment="center",
            fontsize=bigfont,
        )
        fig2.subplots_adjust(
            left=pleft,
            bottom=pbottom,
            right=pright,
            top=0.83,
            wspace=wspace,
            hspace=hspace,
        )

        # ax1 is mean at bottom, ax2 is row number on top
        ax1 = senchar.plot.plt.subplot(1, 1, 1)
        ax1.grid(1)
        ax1.set_ylabel(r"$\rm{Gain\ [e^{-}/DN]}$", fontsize=mediumfont)
        ax1.set_xlabel(r"$\rm{Mean\ [DN]}$", fontsize=mediumfont)
        for label in ax1.xaxis.get_ticklabels():
            label.set_rotation(45)
            label.set_fontsize(smallfont)
        for label in ax1.yaxis.get_ticklabels():
            label.set_fontsize(smallfont)

        ax2 = ax1.twiny()
        ax2.set_xlabel(r"$\rm{Row\ Number}$", fontsize=smallfont)
        ax2.set_xlim(0 + 1, self.num_points + 1)

        # make plots
        for chan in range(self.num_chans):
            # single channel mode
            if self.ext_analyze != -1:
                chan = self.ext_analyze

            # get data into arrays for plotting
            sdev = []
            mm = []
            m = self.means[chan]
            s = self.sdevs[chan]
            g = self.gains[chan]
            gmedian = sorted(g)[len(g) / 2]
            for i in range(self.num_points):
                sdev.append(s[i])
                mm.append(max(m))

            # ptc plot
            senchar.plot.plt.figure(1)
            if self.logplot:
                senchar.plot.plt.loglog(
                    m,
                    sdev,
                    plotstyle[chan % self.num_chans],
                    markersize=marksize,
                )
                senchar.plot.plt.ylim(1)
                senchar.plot.plt.xlim(1, 100000)
            else:
                senchar.plot.plt.plot(
                    m,
                    sdev,
                    plotstyle[chan % self.num_chans],
                    markersize=marksize,
                )
                senchar.plot.plt.ylim(0)
                senchar.plot.plt.xlim(0, 65000)

            # Gain plot
            senchar.plot.plt.figure(2)
            ax2.plot(
                list(range(self.num_points)),
                g,
                plotstyle[chan % self.num_chans],
                markersize=marksize,
            )
            ax1.set_ylim(int(gmedian / 2), gmedian * 2)
            ax1.set_xlim(m[0], m[self.num_points - 1])

            # one pass only for single channel mode
            if self.ext_analyze != -1:
                break

        # save plots
        senchar.plot.save_figure(1, "RampPtc.png")
        senchar.plot.save_figure(2, "RampGain.png")

        return
