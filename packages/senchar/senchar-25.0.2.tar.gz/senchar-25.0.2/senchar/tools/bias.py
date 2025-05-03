import os
import shutil

import numpy

import senchar
import senchar.utils
import senchar.fits
import senchar.image
import senchar.utils
from senchar.plot import plt, save_figure
from senchar.tools.basetool import Tool


class Bias(Tool):
    """
    Bias (zero) image acquisition and analysis.
    """

    def __init__(self):
        super().__init__("bias")

        #: combination method
        self.combination_type = "median"
        #: combined image
        self.superbias_filename = "superbias.fits"
        #: residual image after combined and debiased
        self.debiased_filename = "debiased.fits"

        #: flag to subtract overscan fit from each image
        self.overscan_correct = 0

        self.fit_order = 3
        """fit order for overscan correction"""

        #: bias noise histogram plot
        self.noise_hist_plot = "bias_noise.png"
        #: bias means histogram plot
        self.means_hist_plot = "bias_means.png"
        #: bias cummulative noise histogram plot
        self.cumm_hist_plot = "cumm_hist.png"
        #: bias mean image plot
        self.mean_plot = "mean_image.png"
        #: bias median image plotself.means
        self.median_plot = "median_image.png"
        #: bias noise image plot
        self.sdev_plot = "noise_image.png"

        self.imageplot_scale = 3.0

        #: list of image data from all frames [N][y][x]
        self.datacube = numpy.array

        #: list of senchar images
        self.bias_images = []

        #: list of all bias filenames
        self.bias_filenames = []

        #: mean image
        self.mean_image = []
        #: median image
        self.median_image = []
        #: sdev image
        self.sdev_image = []

        # stats for each extension
        self.mean = []
        self.median = []
        self.sdev = []
        self.mean_noise = []
        self.median_noise = []

        #: output data file
        self.data_file = "bias.txt"
        #: output report file
        self.report_file = "bias"

    def analyze(self):
        """
        Analyze an existing bias series.

        Creates a superbias and a debiased image.
        The superbias image is the median combined iamge and the debiased image
        is then overscan corrected.
        """

        senchar.log("Analyzing bias sequence")

        rootname = "bias."

        # reset parameters
        self.superbias_filename = "superbias.fits"
        self.debiased_filename = "debiased.fits"

        startingfolder = senchar.utils.curdir()
        nextfile, starting_sequence = senchar.utils.find_file_in_sequence(rootname)
        sequence_number = starting_sequence

        # all images must have same image sections
        numext, first_ext, last_ext = senchar.fits.get_extensions(nextfile)
        self._numchans = max(1, numext)

        # create list of all images
        self.bias_filenames = []
        while os.path.exists(nextfile):
            self.bias_filenames.append(nextfile)
            sequence_number = sequence_number + 1
            nextfile = (
                os.path.join(startingfolder, rootname + f"{sequence_number:04d}")
                + ".fits"
            )
            nextfile = senchar.utils.fix_path(nextfile)

        # make assembled images
        self.bias_images = []
        for frame in self.bias_filenames:
            im = senchar.image.Image(frame)
            im.assemble(1)  # assembled an trim overscan
            self.bias_images.append(im)

        # indices are: [imagenum][y][x]
        self.datacube = numpy.stack([im.buffer for im in self.bias_images])

        # create 2D images from stats, index is extension
        self.mean_image = self.datacube.mean(axis=0)
        self.median_image = numpy.median(self.datacube, axis=0)
        self.sdev_image = self.datacube.std(axis=0)

        # get list of status for each ext
        self.mean = self.mean_image.mean()
        self.median = self.median_image.mean()
        self.sdev = self.sdev_image.mean()
        self.mean_noise = self.sdev_image.mean()
        self.median_noise = numpy.median(self.sdev_image)

        # make superbias
        senchar.log(f"Creating superbias image: {self.superbias_filename}")
        senchar.fits.combine(
            self.bias_filenames,
            self.superbias_filename,
            "median",
            overscan_correct=0,
            datatype="uint16",
        )

        # make debiased image (superbias with debias)
        senchar.log(f"Creating debiased image: {self.debiased_filename}")
        if self.overscan_correct == 1:
            shutil.copy(self.superbias_filename, self.debiased_filename)
            senchar.fits.colbias(self.debiased_filename, self.fit_order)
        else:
            senchar.fits.arith(
                self.superbias_filename, "-", self.mean, self.debiased_filename
            )

        self.plot()

        # save absolute filenames
        self.debiased_filename = os.path.abspath(self.debiased_filename)
        self.superbias_filename = os.path.abspath(self.superbias_filename)

        # define dataset
        self.dataset = {
            "data_file": self.data_file,
            "grade": self.grade,
            "debiased_filename": self.debiased_filename,
            "superbias_filename": self.superbias_filename,
            "means": float(self.mean),
            "sdev": float(self.sdev),
            "median": float(self.median),
            "mean_noise": float(self.mean_noise),
            "median_noise": float(self.median_noise),
        }

        # write output files
        senchar.utils.curdir(startingfolder)
        self.write_datafile()
        if self.create_reports:
            self.report()

        # finish
        self.is_valid = 1

    def plot(self):
        """
        Plot bias data.
        """

        # plot noise histogram
        fig, ax = plt.subplots()
        fignum = fig.number
        plt.title("Bias Noise Histogram")
        senchar.plot.move_window(fignum)
        ax = plt.gca()
        min1 = self.sdev_image.min()
        max1 = self.sdev_image.max()
        counts, bins = numpy.histogram(
            self.sdev_image, int(max1) - int(min1) + 1, density=True
        )
        step = bins[1] - bins[0]
        self.counts = counts
        self.bins = bins
        plt.stairs(counts, bins)
        ax.grid(1)
        plt.yscale("log")
        plt.axvline(
            x=self.mean_noise,
            linestyle="dashed",
            color="red",
            label="Mean",
        )
        plt.axvline(
            x=self.median_noise,
            linestyle="dashdot",
            color="black",
            label="Median",
        )
        ax.set_xlabel(f"Noise [DN]")
        ax.set_ylabel("Fraction")
        plt.legend(loc="upper right")
        plt.tight_layout()
        plt.show()
        save_figure(fignum, self.noise_hist_plot)

        # plot cummulative noise histogram
        fig, ax = plt.subplots()
        fignum = fig.number
        plt.title("Cummulative Noise Histogram")
        senchar.plot.move_window(fignum)
        ax = plt.gca()
        f1 = numpy.cumsum(counts) * step
        plt.plot(self.bins[:-1], f1)
        ax.grid(1)
        plt.ylim([0.3, 1.0])
        plt.xlim([0.0, self.sdev_image.mean() * 3])  # 3 sigma plot
        ax.set_xlabel(f"Noise [DN]")
        ax.set_ylabel("Fraction")
        plt.axvline(
            x=self.mean_noise,
            linestyle="dashed",
            color="red",
            label="Mean",
        )
        plt.axvline(
            x=self.median_noise,
            linestyle="dashdot",
            color="black",
            label="Median",
        )
        plt.legend(loc="lower right")
        plt.tight_layout()
        plt.show()
        save_figure(fignum, self.cumm_hist_plot)

        # plot means histogram
        fig, ax = plt.subplots()
        fignum = fig.number
        plt.title("Bias Means Histogram")
        senchar.plot.move_window(fignum)
        ax = plt.gca()
        min1 = self.mean_image.min()
        max1 = self.mean_image.max()
        counts, bins = numpy.histogram(
            self.mean_image, int(max1) - int(min1) + 1, density=True
        )
        plt.stairs(counts, bins)
        ax.grid(1)
        plt.yscale("log")
        ax.set_xlabel(f"Mean [DN]")
        ax.set_ylabel("Fraction")
        plt.axvline(
            x=self.mean,
            linestyle="dashed",
            color="red",
            label="Mean",
        )
        plt.legend(loc="upper right")
        plt.tight_layout()
        plt.show()
        save_figure(fignum, self.means_hist_plot)

        # plot mean image
        fig, ax = plt.subplots()
        fignum = fig.number
        plt.title("Mean Image")
        senchar.plot.move_window(fignum)
        im = plt.imshow(
            self.mean_image,
            cmap="gray",
            vmin=self.mean - self.sdev * self.imageplot_scale,
            vmax=self.mean + self.sdev * self.imageplot_scale,
            interpolation="nearest",
        )
        plt.tight_layout()
        plt.show()
        save_figure(fignum, self.mean_plot)

        # plot median image
        fig, ax = plt.subplots()
        fignum = fig.number
        plt.title("Median Image")
        senchar.plot.move_window(fignum)
        im = plt.imshow(
            self.median_image,
            cmap="gray",
            vmin=self.median - self.sdev * self.imageplot_scale,
            vmax=self.median + self.sdev * self.imageplot_scale,
            interpolation="nearest",
        )
        plt.tight_layout()
        plt.show()
        save_figure(fignum, self.median_plot)

        # plot noise image
        fig, ax = plt.subplots()
        fignum = fig.number
        plt.title("Noise (sdev) Image")
        senchar.plot.move_window(fignum)
        im = plt.imshow(
            self.sdev_image,
            cmap="gray",
            vmin=0.0,
            vmax=self.sdev * 5.0,
            interpolation="nearest",
        )
        plt.tight_layout()
        plt.show()
        save_figure(fignum, self.sdev_plot)

        return

    def report(self):
        """
        Write bias report file.
        """

        lines = ["# Bias Analysis", ""]

        if self.grade != "UNDEFINED":
            lines.append(f"Bias grade = {self.grade}  ")

        s = "|**Mean (DN)**|**Noise (DN)**|"
        lines.append(s)
        s = "|:---:|:---:|"
        lines.append(s)

        s = f"|{self.mean:.0f}|{self.sdev:.01f}|"
        lines.append(s)
        lines.append("")

        lines.append(
            f"![Bias Noise Histogram]({os.path.abspath(self.noise_hist_plot)})  "
        )
        lines.append("*Bias noise histogram.*  ")

        lines.append(
            f"![Bias Means Histogram]({os.path.abspath(self.means_hist_plot)})  "
        )
        lines.append("*Bias means histogram.*  ")

        lines.append(
            f"![Bias Cummulative Noise Histogram]({os.path.abspath(self.cumm_hist_plot)})  "
        )
        lines.append("*Bias cummulative noise histogram.*  ")

        lines.append(f"![Bias Noise Image]({os.path.abspath(self.sdev_plot)})  ")
        lines.append("*Bias Noise (sdev) image plot.*  ")

        if 1:
            lines.append(f"![Bias Mean Image]({os.path.abspath(self.mean_plot)})  ")
            lines.append("*Bias mean image plot.*  ")

            lines.append(f"![Bias Median Image]({os.path.abspath(self.median_plot)})  ")
            lines.append("*Bias median image plot.*  ")

        # Make report files
        self.write_report(self.report_file, lines)

        return
