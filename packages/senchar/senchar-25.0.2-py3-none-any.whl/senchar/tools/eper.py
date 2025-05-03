import numpy
from astropy.io import fits as pyfits

import senchar
import senchar.utils
import senchar.fits
from senchar.tools.basetool import Tool


class Eper(Tool):
    """
    EPER - Extended Pixel Edge Response analysis.
    """

    def __init__(self):
        super().__init__("eper")

        self.grade_vcte = "UNDEFINED"
        self.grade_hcte = "UNDEFINED"

        self.data_file = "eper.txt"
        self.report_file = "eper"

        self.number_prescan_rows = 0
        self.number_prescan_cols = 0
        self.number_bias_rows = 0  # rows to use for counting signal in overscan
        self.number_bias_cols = 0  # cols to use for counting signal in overscan

        self.dark_correct = 0
        self.dark_file = ""

        self.filename = "superflat"
        self.limit_hcte = 0.999995
        self.limit_vcte = 0.999995

        self.reject_scale = 3.0  # reject pixel x times above mean

        self.hcte = []
        self.vcte = []

        return

    def analyze(self):
        """
        Analyze an exisiting SuperFlat image set for EPER.
        """

        senchar.log("Analyzing EPER sequence")

        filename = senchar.utils.make_image_filename(self.filename)

        startingfolder = senchar.utils.curdir()

        # get image info
        _, first_ext, last_ext = senchar.fits.get_extensions(filename)

        # get image data (superflat is already bias corrected)
        eperim = pyfits.open(filename)

        if self.dark_correct:
            darkim = pyfits.open(self.dark_file)  # assume scaled correctly for now
            self.darkim = darkim

        # CTE is 1.0 - (Signal Overscan1 + Overscan2) / (Signal Last Row/Col) / (total shifts)

        # process each channel
        self.vcte = []
        self.hcte = []
        self.MeanData = []

        self.imbufs = []
        self.darkbufs = []

        for chan, ext in enumerate(range(first_ext, last_ext)):
            # get this image section size (all zero based)
            hdr = eperim[ext].header
            ncols = hdr["NAXIS1"]
            nrows = hdr["NAXIS2"]

            FirstBiasCol, _, FirstBiasRow, LastBiasRow = senchar.fits.get_section(
                filename, "BIASSEC", chan + 1
            )

            _, LastDataCol, _, LastDataRow = senchar.fits.get_section(
                filename, "DATASEC", chan + 1
            )

            # BIASSEC keyword does not contain overscan row info
            FirstBiasRow = LastDataRow + 1

            # get bias subtracted data as [rows,cols]
            imbuf = numpy.reshape(eperim[ext].data, [nrows, ncols])

            if self.dark_correct:
                darkbuf = numpy.reshape(darkim[ext].data, [nrows, ncols])
                self.darkbufs.append(darkbuf)
                self.imbufs.append(imbuf)
                imbuf = imbuf - darkbuf

            # vcte
            numvshifts = LastDataRow + 1 + self.number_prescan_rows

            vdata = imbuf[LastDataRow, :]
            sumvdata = vdata.sum()
            meanvdata = sumvdata / len(vdata)  # mean per pixel, should remove cols also

            vbias = imbuf[FirstBiasRow : FirstBiasRow + self.number_bias_rows + 1, :]
            vbias = vbias.sum(0)
            vbiasmean = vbias.mean()
            # senchar.log('vbias mean is',vbiasmean)

            # reject column defects, replace bias pixels > 3x mean
            for i, value in enumerate(vbias):
                if value > self.reject_scale * vbiasmean:
                    senchar.log(
                        "VCTE rejecting bad pixel - chan: {chan}, column: {i}, value: {value:0.0f}"
                    )
                    vbias[i] = vbiasmean  # replace defective pixels with mean
            sumvbias = max(vbias.sum(), 0.0)

            vcte = 1.0 - sumvbias / sumvdata / numvshifts
            vcte = min(vcte, 1.0)

            # hcte
            numhshifts = LastDataCol + 1 + self.number_prescan_cols

            # sumhdata=imbuf[:,LastDataCol].sum()
            sumhdata = imbuf[0:LastBiasRow, LastDataCol].sum()
            meanhdata = sumhdata / len(
                imbuf[0:LastBiasRow, LastDataCol]
            )  # mean per pixel

            # sumhbias=imbuf[:,FirstBiasCol:FirstBiasCol+self.number_bias_cols+1].sum()
            sumhbias = imbuf[
                0:LastBiasRow, FirstBiasCol : FirstBiasCol + self.number_bias_cols + 1
            ].sum()
            sumhbias = max(sumhbias, 0.0)
            meanhbias = sumhbias / len(
                imbuf[
                    0:LastBiasRow,
                    FirstBiasCol : FirstBiasCol + self.number_bias_cols + 1,
                ]
            )

            hcte = 1.0 - meanhbias / meanhdata / numhshifts
            hcte = min(hcte, 1.0)

            self.hcte.append(hcte)
            self.vcte.append(vcte)
            meandata = (meanhdata + meanvdata) / 2.0
            self.MeanData.append(meandata)

        # log results
        for chan, vcte in enumerate(self.vcte):
            senchar.log(f"Chan. {chan:02d} VCTE: {vcte:.06f}")
        for chan, hcte in enumerate(self.hcte):
            senchar.log(f"Chan. {chan:02d} HCTE: {hcte:.06f}")

        # grade entire device
        hcte1 = numpy.array(self.hcte).min()
        vcte1 = numpy.array(self.vcte).min()
        if hcte1 >= self.limit_hcte:
            self.grade_hcte = "PASS"
        else:
            self.grade_hcte = "FAIL"

        if vcte1 >= self.limit_vcte:
            self.grade_vcte = "PASS"
        else:
            self.grade_vcte = "FAIL"

        senchar.log(f"Grade VCTE = {self.grade_vcte}")
        senchar.log(f"Grade HCTE = {self.grade_hcte}")

        if self.grade_hcte == "PASS" and self.grade_vcte == "PASS":
            self.grade = "PASS"
        else:
            self.grade = "FAIL"
        senchar.log(f"Grade = {self.grade}")

        # define dataset
        self.dataset = {
            "data_file": self.data_file,
            "grade": self.grade,
            "grade_hcte": self.grade_hcte,
            "hcte": self.hcte,
            "grade_vcte": self.grade_vcte,
            "vcte": self.vcte,
            "MeanData": self.MeanData,
        }

        # write output files
        senchar.utils.curdir(startingfolder)
        self.write_datafile()
        if self.create_reports:
            self.report()

        # close file
        eperim.close()

        self.is_valid = 1

        return

    def report(self):
        """
        Write report file.
        """

        lines = ["# EPER Analysis"]

        s = f"EPER grade = {self.grade}  "
        lines.append(s)
        s = f"EPER HCTE grade = {self.grade_hcte}  "
        lines.append(s)
        s = f"EPER VCTE grade = {self.grade_vcte}  "
        lines.append(s)

        s = f"HCTE limit = {self.limit_hcte:0.06f}  "
        lines.append(s)
        s = f"VCTE limit = {self.limit_vcte:0.06f}  "
        lines.append(s)

        mean = numpy.array(self.MeanData).mean()
        lines.append(f"Mean Signal Level: {mean:7.0f} DN  ")
        lines.append("")

        lines.append("")
        s = f"|**Channel**|**HCTE**|**VCTE**|"
        lines.append(s)
        s = "|:---|:---:|:---:|"
        lines.append(s)

        for chan in range(len(self.hcte)):
            hcte = self.hcte[chan]
            vcte = self.vcte[chan]
            s = f"|{chan:02d}|{hcte:8.06f}|{vcte:8.06f}|"
            lines.append(s)

        # Make report files
        self.write_report(self.report_file, lines)

        return
