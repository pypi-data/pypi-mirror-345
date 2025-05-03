import datetime
import os
import subprocess

import senchar
import senchar.utils
from senchar.tools.report import Report
from senchar.tools.tools import Tool


class DetChar(Tool, Report):
    """
    Base DetChar class.
    """

    def __init__(self):
        Tool.__init__(self, "detchar")
        Report.__init__(self)

        self.package_id = ""
        self.camera_id = ""

        self.summary_lines: list[str] = []
        self.summary_report_name: str = "SummaryReport"
        self.report_date: str = ""
        self.report_comment: str = ""
        self.operator: str = ""
        self.system: str = ""
        self.customer: str = ""
        self.is_setup = False

    def setup(self, camera_id: str = ""):
        """
        Setup for acquistion and analysis
        """

        raise NotImplementedError("setup() not implemented")

    def make_report(self):
        """
        Make detector characterization report.
        """

        if not self.is_setup:
            self.setup()

        folder = senchar.utils.curdir()
        self.report_folder = folder

        print(f"Generating {self.report_name}")

        # *********************************************
        # Combine PDF report files for each tool
        # *********************************************
        rfiles = [self.summary_report_name + ".pdf"]
        for r in self.report_names:  # add pdf extension
            f1 = self.report_files[r] + ".pdf"
            f1 = os.path.abspath(f1)
            if os.path.exists(f1):
                rfiles.append(f1)
            else:
                print("Report file not found: %s" % f1)
        self.merge_pdf(rfiles, f"{self.report_name}.pdf")

        # open report
        with open(os.devnull, "w") as fnull:
            s = f"{self.report_name}pdf"
            subprocess.Popen(s, shell=True, cwd=folder, stdout=fnull, stderr=fnull)
            fnull.close()

        return

    def make_summary_report(self):
        """
        Create a ID and summary report.
        """

        if not self.is_setup:
            self.setup()

        if len(self.report_comment) == 0:
            self.report_comment = senchar.utils.prompt("Enter report comment")

        # get current date
        self.report_date = datetime.datetime.now().strftime("%b-%d-%Y")

        """
        # example
        
        self.summary_lines = []

        self.summary_lines.append("# 90prime Detector Characterization Report")

        self.summary_lines.append("|||")
        self.summary_lines.append("|:---|:---|")
        self.summary_lines.append(f"|Customer       |UArizona|")
        self.summary_lines.append(f"|ITL System     |90prime|")
        self.summary_lines.append(f"|ITL ID         |{self.camera_id}|")
        self.summary_lines.append(f"|Report Date    |{report_date}|")
        self.summary_lines.append(f"|Operator       |{self.operator}|")
        self.summary_lines.append(f"|System         |{self.system}|")
        """

        lines = []
        lines.append(f"|Comment        |{self.report_comment}|")
        lines.append(f"|Report date    |{self.report_date}|")

        # Make report files
        senchar.log(f"Generating {self.summary_report_name}.pdf")
        self.write_report(self.summary_report_name, self.summary_lines, lines)

        return

    def upload_prep(self, shipdate: str):
        """
        Prepare a dataset for upload by creating an archive file.
        file.  Start in the _shipment folder.
        """

        startdir = senchar.utils.curdir()
        shipdate = os.path.basename(startdir)
        idstring = f"{shipdate}"

        # cleanup folder
        senchar.log("cleaning dataset folder")
        itlutils.cleanup_files()

        # move one folder above report folder
        # senchar.utils.curdir(reportfolder)
        # senchar.utils.curdir("..")

        self.copy_files()

        # copy files to new folder and archive
        senchar.log(f"copying dataset to {idstring}")
        currentfolder, newfolder = senchar.utils.make_file_folder(idstring)

        copy_files = glob.glob("*.pdf")
        for f in copy_files:
            shutil.move(f, newfolder)
        copy_files = glob.glob("*.fits")
        for f in copy_files:
            shutil.move(f, newfolder)
        copy_files = glob.glob("*.csv")
        for f in copy_files:
            shutil.move(f, newfolder)

        senchar.utils.curdir(newfolder)

        # make archive file
        senchar.utils.curdir(currentfolder)
        senchar.log("making archive file")
        archivefile = itlutils.archive(idstring, "zip")
        shutil.move(archivefile, newfolder)

        # delete data files from new folder
        senchar.utils.curdir(newfolder)
        [os.remove(x) for x in glob.glob("*.pdf")]
        [os.remove(x) for x in glob.glob("*.fits")]
        [os.remove(x) for x in glob.glob("*.csv")]

        senchar.utils.curdir(startdir)

        self.remote_upload_folder = idstring

        return archivefile
