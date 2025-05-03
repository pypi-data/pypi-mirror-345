import json

import senchar
from senchar.tools.report import Report


class Tool(Report):
    """
    Base class inherited by tool classes.
    """

    def __init__(self, tool_id, description=None):

        Report.__init__(self)

        self.camera_id = ""
        """ID of camera under test"""

        self.number_images_acquire = 1
        """number of images to acquire"""

        self.rootname = "tool."
        """root for data filenames"""

        # analysis
        self.grade = "UNDEFINED"
        """final grade"""

        self.grade_sensor = True
        """True to produce a grade"""

        self.is_valid = False
        """True if analysis results are valid"""

        self.data_file = "base.txt"
        """output data file"""

        self.dataset = {}
        """output data set to be written to datafile"""

        #: output report file
        self.report_file = "base"
        """no extension, will be pdf or md"""

        self.create_reports = True
        """True to generate reports during analysis"""

        self.create_plots = True
        """True to generate plots during analysis"""

        # all tools are initialized and reset at creation
        self.initialize()
        self.reset()

        # add tool to dict
        senchar.db.tools[tool_id] = self

    def initialize(self):
        """
        Initialize tool.
        """

        self.is_initialized = 1

        return

    def reset(self):
        """
        Reset tool.
        """

        self.is_reset = 1

        return

    def analyze(self):
        """
        Analyze data.
        """

        raise NotImplementedError("analyze() not defined")

    def write_datafile(self):
        """
        Write data file as a json dump.

        Note: numpy.array(x).tolist() may be useful for dataset.
        """

        with open(self.data_file, "w") as datafile:
            json.dump(self.dataset, datafile)

        return

    def read_datafile(self, filename="default"):
        """
        Read an existing data file and set tool as valid.
        """

        if filename == "prompt":
            f = senchar.utils.file_browser(
                self.data_file, [("data files", ("*.txt"))], Label="Select data file"
            )
            if f is not None and f != "":
                self.data_file = f[0]
        elif filename == "default":
            filename = self.data_file

        # read file
        with open(filename, "r") as datafile:
            dataline = datafile.readlines()

        self.dataset = json.loads(dataline[0])

        for data in self.dataset:
            setattr(self, data, self.dataset[data])

        self.is_valid = True

        return

    def report(self):
        """
        Generate a report.
        """

        raise NotImplementedError("report() not defined")
