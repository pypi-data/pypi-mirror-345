"""
*senchar.utils* contains general purpose support commands used throughout senchar.
"""

import os
import shlex
import sys
import importlib
import importlib.util
from typing import List, Any

from PySide6.QtWidgets import QFileDialog

if os.name == "nt":
    import winsound

import senchar
import senchar.utils
import senchar.exceptions


# keyboard checking is optional
try:
    import msvcrt
except Exception:
    pass


def curdir(folder: str = "") -> str:
    """
    Gets and sets the working folder.
    If folder is not specified then just return the current working folder.

    Args:
        folder: name of folder set.
    Returns:
        the current folder (after changing).
    """

    if folder is None:
        return

    if folder != "":
        folder = folder.lstrip('"').rstrip('"')
        try:
            os.chdir(folder)
        except FileNotFoundError:
            pass

    reply = os.getcwd()

    reply = reply.replace("\\", "/")

    senchar.db.wd = reply  # save result

    return reply


def fix_path(path: str = "", no_drive_letter: bool = True) -> str:
    """
    Makes a nice absolute path, leaving only forward slashes.

    Args:
        path: name of path to cleanup.
        no_drive_letter: Removes leading drive letter.
    Returns:
        cleaned path name.
    """

    if os.name != "posix":
        norm = os.path.abspath(os.path.normpath(path))
        pth = norm.replace("\\", "/")  # go to forward slashes only
        if no_drive_letter and len(pth) > 2 and pth[1] == ":":
            pth = pth[2:]
    else:
        pth = os.path.expanduser(path)
        pth = os.path.normpath(pth)

    return pth


def add_searchfolder(search_folder: str = "", include_subfolders: bool = True) -> None:
    """
    Appends search_folder (and by default all its subfolders) to the current python search path.
    Default is current folder and its subfolders.
    Subfolders beginning with "_" are not included.

    Args:
        search_folder: Name of folder to add to sys.path
        include_subfolders: True to include all subfolders in sys.path
    """

    if search_folder == "":
        search_folder = curdir()

    search_folder = fix_path(search_folder)

    # append all subfolders of search_folder to current search path
    if search_folder not in sys.path:
        sys.path.append(search_folder)

    if include_subfolders:
        for root, dirs, _ in os.walk(search_folder):
            if dirs:
                for s in dirs:
                    if s.startswith("_"):
                        continue
                    sub = os.path.join(root, s)
                    sub = fix_path(sub)
                    if sub not in sys.path:
                        sys.path.append(sub)

    return


def make_image_filename(imagefile: str) -> str:
    """
    Returns the absolute file imagefile, with forward slashes.
    Appends ".fits" if no extension is included.

    Args:
        imagefile: image filename to be expanded
    Returns:
        expanded image filename.
    """

    if imagefile.endswith(".fits"):
        pass
    elif imagefile.endswith(".fit"):
        pass
    elif not imagefile.endswith(".bin"):
        imagefile += ".fits"

    return fix_path(imagefile)


def parse(string: str, set_type: bool = False) -> List[str]:
    """
    Parse a string into tokens using the standard senchar rules.
    If setType is true, try and set data data type for each token.

    Args:
        string: String to be parsed into tokens
        set_type: True to try and set the type of each token ("1" to 1)
    Returns:
        list of parsed tokens
    """

    # allow for quotes
    lex = shlex.shlex(string)
    lex.quotes = "\"'"
    lex.whitespace_split = True
    lex.commenters = "#"
    toks = list(lex)

    # remove bounding quotes unless quoting a number (leave as string)
    tokens = []
    for tok in toks:
        if tok.startswith('"') and tok.endswith('"'):
            tok1 = tok[1:-1]
            # t, value = get_datatype(tok1)
            # if t not in ["int", "float"]:
            #     tok = tok1

        elif tok.startswith("'") and tok.endswith("'"):
            tok1 = tok[1:-1]
            # t, value = get_datatype(tok1)
            # if t not in ["int", "float"]:
            #     tok = tok1

        tokens.append(tok)

    if set_type:
        for i, tok in enumerate(tokens):
            t, value = get_datatype(tok)
            tokens[i] = value

    return tokens


def get_datatype(value: Any) -> list:
    """
    Determine the data type for an object and set the type if possible. A string such as "1.23"
    will result in a type "float" and "2" will result in type "int".

    Args:
        value: object to be typed
    Returns:
        list [type, value] of data type as a code and object with that type
    """

    if isinstance(value, str):
        # string integer
        if value.isdigit():
            attributetype = "int"
            value = int(value)
            return [attributetype, value]
        else:
            try:
                value = float(value)
                attributetype = "float"
                return [attributetype, value]
            except ValueError:
                pass

        attributetype = "str"

    elif isinstance(value, int):
        attributetype = "int"
        value = int(value)

    elif isinstance(value, float):
        attributetype = "float"
        value = float(value)

    # more work here
    else:
        attributetype = "str"

    return [attributetype, value]


def prompt(prompt_message: str = "Enter a string", default: Any = "") -> Any:
    """
    Prints a message and waits for user input.

    Args:
        prompt_message: string to be printed
        default:  string to be returned if no value is entered
    Returns:
        string entered or default value
    """

    default = str(default)
    try:
        if default != "":
            in1 = input(prompt_message + " [" + default + "]: ")
        else:
            in1 = input(prompt_message + ": ")
    except KeyboardInterrupt:
        return ""

    if in1 == "":
        return default
    else:
        return in1


def check_keyboard(wait: bool = False) -> str:
    """
    Checks keyboard for a key press.
    For Windows OS only.

    Args:
        wait: True to wait until a key is pressed
    Returns:
        key which was pressed or empty string.
    """

    # TODO: map sequences like 'F1'

    if os.name != "nt":
        raise senchar.exceptions.SencharError("check_keyboard not supported on this OS")

    loop = 1
    key = ""

    while loop:
        if msvcrt.kbhit():
            key = msvcrt.getch()
            try:
                key = key.decode()

                # since the key is byte type, maybe escape sequence so check for more
                # if msvcrt.kbhit():
                #    key1 = msvcrt.getch()
                #    # key = key + key1.decode()
            except UnicodeDecodeError:
                pass
            break
        if not wait:
            loop = 0

    return key


def show_menu(configs: dict) -> str:
    """
    Interative: Show a menu and wait for selection.
    "blank" may be used to display an empty line.
    print() is allowed here as this is for interactive use only.

    Args:
        configs: Dictionary of strings which are menu items
    Returns:
        string associated with item selected or empty string.
    """

    if len(configs) == 1:
        choice = configs[list(configs.keys())[0]]
        return choice

    CONFIRMED = 0
    choice = ""
    while not CONFIRMED:
        print("Select configuration number from list below:\n")
        i = 0
        for c in configs:
            if c == "blank":
                print("")
            else:
                i += 1
                print("%1d.....%s" % (i, c))
        print("")
        print("Enter configuration number: ", end="")
        choiceindex = input()
        if choiceindex == "q":
            senchar.exceptions.warning("Quit detected")
            return
        try:
            choiceindex = int(choiceindex)
        except ValueError:
            print("Bad keyboard input...try again\n")
            continue

        choiceindex = int(choiceindex)
        choiceindex = choiceindex - 1  # zero based

        # remove blanks
        for x in configs:
            if x == "blank":
                configs.remove("blank")

        if choiceindex < 0 or choiceindex > len(configs) - 1:
            print("invalid selection - %d\n" % (choiceindex + 1))
            continue

        # get choice
        configlist = list(configs.keys())  # is order OK?
        choice = configs[configlist[choiceindex]]

        CONFIRMED = 1

    print("")

    return choice


def get_datafolder(datafolder: str | None = None):
    """
    Return the datafolder for this system.
    If not specified, root is /data on Windows or ~/data on Linux.
    """

    if datafolder is None:
        droot = os.environ.get("senchar_DATAROOT")
        if droot is None:
            if os.name == "posix":
                droot = os.environ.get("HOME")
            else:
                droot = "/"
            datafolder = os.path.join(
                os.path.realpath(droot), "data", senchar.db.systemname
            )
        else:
            datafolder = os.path.join(os.path.realpath(droot), senchar.db.systemname)
    else:
        datafolder = os.path.realpath(datafolder)

    datafolder = os.path.normpath(datafolder)

    return datafolder


def dequote(input: str) -> str:
    """
    Remove matching single or double quote at ends of input.

    Args:
        input: string to be dequoted.
    """

    if type(input) != str:
        return input

    if input.startswith("'") and input.endswith("'"):
        dequote = input[1:-1]
    elif input.startswith('"') and input.endswith('"'):
        dequote = input[1:-1]
    else:
        dequote = input

    return dequote


def quoter(input: str) -> str:
    """
    Put quotes around a string if it contains special characters.
    Currently just spaces.

    Args:
        input: string to be optionally quoted.
    """

    if type(input) != str:
        return input

    if " " not in input:
        return input

    if input.startswith("'") and input.endswith("'"):
        output = input
    elif input.startswith('"') and input.endswith('"'):
        output = input
    else:
        output = f'"{input}"'

    return output


def beep(frequency=2000, duration=500) -> None:
    """
    Play a sound.
    Install beep on Linux systems.
    """

    if os.name == "posix":
        os.system("beep -f %s -l %s" % (frequency, duration))
    else:
        winsound.Beep(frequency, duration)

    return


def find_file_in_sequence(file_root: str, file_number: int = 1) -> tuple:
    """
    Returns the Nth file in an image sequence where N is file_number (1 for first file).

    Args:
        file_root: image file root name.
        file_number: image file number in sequence.

    Returns:
        tuple (filename,sequencenumber).
    """

    currentfolder = senchar.utils.curdir()

    for _, _, files in os.walk(currentfolder):
        break

    for f in files:
        if f.startswith(file_root):
            break

    try:
        if not f.startswith(file_root):
            raise senchar.exceptions.SencharError("image sequence not found")
    except Exception:
        raise senchar.exceptions.SencharError("image sequence not found")

    firstfile = senchar.utils.fix_path(os.path.join(currentfolder, f))
    firstsequencenumber = firstfile[-9:-5]
    firstnum = firstsequencenumber
    firstsequencenumber = int(firstsequencenumber)
    sequencenumber = firstsequencenumber + file_number - 1
    newnum = "%04d" % sequencenumber
    filename = firstfile.replace(firstnum, newnum)

    return (filename, sequencenumber)


def make_file_folder(
    subfolder: str, increment: bool = True, use_number: bool = False
) -> tuple:
    """
    Creates a new subfolder in the current FileFolder.

    Args:
        subfolder: subfolder name to create
        increment: - if True, subfolder name may be incremented to create a unique name
        use_number: - if True, starts with '1' after Subfolder name (e.g. report1 not report)
    Returns:
        tuple (currentfolder,newfolder)
    """

    currentfolder = senchar.utils.curdir()

    sf = subfolder + "1" if use_number else subfolder

    try:
        newfolder = os.path.join(currentfolder, sf)  # new subfolder
        os.mkdir(newfolder)
        newfolder = senchar.utils.fix_path(newfolder)
    except Exception:
        if not increment:
            raise senchar.exceptions.SencharError("could not make new subfolder")
        else:
            for i in range(1, 1000):
                newfolder = os.path.join(
                    currentfolder, subfolder + str(i)
                )  # try a new subfolder name
                try:
                    os.mkdir(newfolder)
                    newfolder = senchar.utils.fix_path(newfolder)
                    break
                except Exception:  # error OK
                    continue
            if i == 999:
                raise senchar.exceptions.SencharError("could not make subfolder")

    newfolder = senchar.utils.fix_path(newfolder)

    return (currentfolder, newfolder)


def get_image_roi() -> list:
    """
    Get the data and noise regions of interest in image image coordinates.
    Check for ROI's in the following order:
      - senchar.db.imageroi if defined
      - display.roi if defined

    Returns:
        list of ROIs
    """

    # database roi
    if senchar.db.get("imageroi"):
        if senchar.db.imageroi != []:
            return senchar.db.imageroi

    # display.roi
    roi = []

    try:
        reply = senchar.db.tools["display"].get_rois(0, "image")
    except AttributeError:
        raise senchar.exceptions.SencharError("cannot get ROI - display not found")
    roi.append(reply)
    reply = senchar.db.tools["display"].get_rois(1, "image")
    if reply:
        roi.append(reply)
    else:
        roi.append(roi[0])

    return roi


def set_image_roi(roi: list = []) -> None:
    """
    Set the global image region of interest "db.imageroi".
    If roi is not specified, use display ROI.

    Args:
        roi: ROI list or []
    """

    # set directly with given value
    if roi != []:
        senchar.db.imageroi = roi
        return

    # use display ROIs
    roi = []
    try:
        reply = senchar.db.tools["display"].get_rois(-1, "image")
    except AttributeError:
        raise senchar.exceptions.SencharError("cannot set ROI - no display found")

    if not reply:
        raise senchar.exceptions.SencharError("could not get display ROI")

    senchar.db.imageroi = reply

    return


def get_tools(tool_names: list) -> list:
    """
    Return a list of tool objects from a list of their names.

    Args:
        tool_names: list of the tool names to get

    Returns:
        list of tool objects
    """

    tools = []

    for tool in tool_names:
        tool1 = senchar.db.tools[tool]
        if tool1 is not None:
            tools.append(tool1)
        else:
            tools.append(senchar.db.tools(tool))

    return tools


def find_file(filename: str, include_curdir: bool = False) -> str:
    """
    Find the absolute filename for a file in the current search path.
    Set include_curdir True to add curdir() to search path.

    Args:
        filename: Name of file.
        include_curdir: True to include current folder in sys.path.
    Returns:
        Cleaned path name
    Raises:
        FileNotFoundError if file not found.

    """

    added_cd = 0
    if include_curdir:
        cd = senchar.utils.curdir()
        if cd not in sys.path:
            sys.path.append(cd)
            added_cd = 1

    # absolute pathname
    if os.path.isabs(filename):
        if added_cd:
            sys.path.remove(cd)
        if os.path.exists(filename):
            return filename
        else:
            raise FileNotFoundError(f'file "{filename}" not found')

    file_found = 0
    for path in sys.path:
        if path == "":
            pass
        elif os.path.exists(os.path.join(path, filename)):
            if os.path.isdir(os.path.join(path, filename)):  # no folders
                continue
            file_found = 1
            break
    if added_cd:
        sys.path.remove(cd)

    if file_found:
        return os.path.normpath(os.path.join(path, filename))
    else:
        raise FileNotFoundError(f'file "{filename}" not found')

    return


def file_browser(
    path: str = "", select_string: str = "*.*", label: str = ""
) -> list | None:
    """
    Filebrowser GUI to select files.  This is the Qt version.

    Args:
        path: Starting path for selection.
        select_string: Selection string like [('all files',('*.*'))] or *folder* to select folders.
        label: Dialog window label.
    Returns:
        list of selected files/folders or None
    """

    if select_string == "folder":
        data = QFileDialog.getExistingDirectory(caption=label, dir=path)
        if data == "":
            data = None
        else:
            data = [data]
    else:
        data = QFileDialog.getOpenFileNames(
            caption=label,
            dir=path,
            filter=select_string,
        )
        if data[0] == []:
            data = None
        else:
            data = data[0]

    return data


def bf():
    """Shortcut for file_browser()."""

    folder = file_browser("", "folder", "Select folder")
    if folder == []:
        return
    if isinstance(folder, list):
        folder = folder[0]
    curdir(folder)

    return folder


def sroi():
    """Shortcut for set_image_roi()."""
    set_image_roi()


def load_scripts(package_list: list = [], folder_list: list = []) -> None:
    """
    Load scripts from a list of packages and/or a list of folders, into senchar.db.scripts.
    """

    folders = []
    for package in package_list:
        spec = importlib.util.find_spec(package)
        if spec is not None:
            folder = spec.submodule_search_locations[0]
            folders.append(folder)
            continue

    pyfiles = []
    for folder in folders:

        # bring all .py modules with same function name into namespace
        _, _, filenames = next(os.walk(folder))
        for file1 in filenames:
            if file1.endswith(".py"):
                pyfiles.append(file1[:-3])
        if "__init__" in pyfiles:
            pyfiles.remove("__init__")

        for pfile in pyfiles:
            try:
                mod = importlib.import_module(f"{package}.{pfile}")
                func = getattr(mod, pfile)
                senchar.db.scripts[pfile] = func
            except Exception as e:
                senchar.log(e)
                senchar.exceptions.warning(f"Could not import script {pfile}")

    folders = []
    pyfiles = []
    for folder in folder_list:

        sys.path.append(folder)
        _, _, filenames = next(os.walk(folder))
        for file1 in filenames:
            if file1.endswith(".py"):
                pyfiles.append(file1[:-3])
        if "__init__" in pyfiles:
            pyfiles.remove("__init__")
        folders.append(folder)

        for pfile in pyfiles:
            try:
                mod = importlib.import_module(f"{pfile}")
                func = getattr(mod, pfile)
                senchar.db.scripts[pfile] = func
            except Exception as e:
                senchar.log(e)
                senchar.exceptions.warning(f"Could not import script {pfile}")

    return
