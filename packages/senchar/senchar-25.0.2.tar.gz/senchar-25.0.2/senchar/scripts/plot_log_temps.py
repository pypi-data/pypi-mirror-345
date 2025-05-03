"""
Plot temperatures from logfile when tempcon.log_temps=1.
"""

import sys

import senchar
import senchar.utils
import senchar.plot


def plot_log_temps(samplestep=1, tickstep=1):
    """
    Plot camtemp and dewtemp from log file.
    """

    samplestep = int(samplestep)
    tickstep = int(tickstep)

    # setup plot
    fig, ax = senchar.plot.plt.subplots(constrained_layout=True)
    ax.grid(1)
    senchar.plot.plt.title("Temperatures")
    senchar.plot.plt.ylabel("Temperature [C]")
    senchar.plot.plt.xlabel("Time")

    with open("/data/temperatures.log", "r") as logfile:
        lines = logfile.readlines()

    # read every samplestep templog lines
    linenums = []
    sample = samplestep
    for linenum, line in enumerate(lines):
        if "templog:" in line:
            sample -= 1
            if sample == 0:
                linenums.append(linenum)
                sample = samplestep

    times = []
    camtemps = []
    dewtemps = []
    print("Time\t\tCamtemp\tDewtemp")
    for linenum in linenums:
        s = f"{lines[linenum].strip()}"
        tokens = senchar.utils.parse(s)
        camtemp = float(tokens[-4])
        camtemps.append(camtemp)
        dewtemp = float(tokens[-3])
        dewtemps.append(dewtemp)
        timestamp = tokens[1][:-4]  # remove msec
        times.append(timestamp)

        print(f"{timestamp}\t{camtemp:.1f}\t{dewtemp:.1f}")

        senchar.plot.plt.plot(times, camtemps, senchar.plot.style_lines[0])
        senchar.plot.plt.plot(times, dewtemps, senchar.plot.style_lines[1])

    senchar.plot.plt.xticks(
        times[::tickstep], rotation=90
    )  # adjust step size as needed

    return


if __name__ == "__main__":
    args = sys.argv[1:]
    plot_log_temps(*args)
