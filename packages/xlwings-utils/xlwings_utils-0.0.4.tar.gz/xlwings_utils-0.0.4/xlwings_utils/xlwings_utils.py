#         _            _                                   _    _  _
#  __  __| |__      __(_) _ __    __ _  ___         _   _ | |_ (_)| | ___
#  \ \/ /| |\ \ /\ / /| || '_ \  / _` |/ __|       | | | || __|| || |/ __|
#   >  < | | \ V  V / | || | | || (_| |\__ \       | |_| || |_ | || |\__ \
#  /_/\_\|_|  \_/\_/  |_||_| |_| \__, ||___/ _____  \__,_| \__||_||_||___/
#                                |___/      |_____|

__version__ = "0.0.4"


import dropbox
from pathlib import Path
import os

class BlockRange:
    @property
    def block(self):
        return block(self.value)

    @block.setter
    def block(self, block):
        self.value=block.as_list_of_lists
try:
    import xlwings
    xlwings.Range.block=BlockRange
except ImportError:
    ...

_captured_stdout = []
dbx = None


def dropbox_init(refresh_token=None, app_key=None, app_secret=None):
    """
    dropbox initialize

    This function has to be called prior to using any dropbox function

    Parameters
    ----------
    refresh_token : str
        oauth2 refreshntoken

        if omitted: use the environment variable REFRESH_TOKEN

    app_key : str
        app key

        if omitted: use the environment variable APP_KEY


    app_secret : str
        app secret

        if omitted: use the environment variable APP_SECRET

    Returns
    -------
    -
    """
    if refresh_token is None:
        refresh_token = os.environ["REFRESH_TOKEN"]
    if app_key is None:
        app_key = os.environ["APP_KEY"]
    if app_secret is None:
        app_secret = os.environ["APP_SECRET"]

    global dbx
    dbx = dropbox.Dropbox(oauth2_refresh_token=refresh_token, app_key=app_key, app_secret=app_secret)


def _check_dbx():
    if dbx is None:
        raise ValueError("not initialized. Please call dropbox_init()")


def list_dropbox(path="", recursive=False):
    """
    list_dropbox

    returns all dropbox files in path

    Parameters
    ----------
    path : str or Pathlib.Path
        path from which to list all files (default: '')


    recursive : bool
        if True, recursively list files. if False (default) no recursion

    Returns
    -------
    files, relative to path : list
    """
    _check_dbx()
    out = []
    result = dbx.files_list_folder(path, recursive=recursive)

    for entry in result.entries:
        if isinstance(entry, dropbox.files.FileMetadata):
            out.append(entry.path_display)

    while result.has_more:
        result = dbx.files_list_folder_continue(result.cursor)
        for entry in result.entries:
            if isinstance(entry, dropbox.files.FileMetadata):
                out.append(entry.path_display)

    return out


def read_dropbox(dropbox_path):
    """
    read_dropbox

    read from dopbox at given path

    Parameters
    ----------
    dropbox_path : str or Pathlib.Path
        path to read from

    Returns
    -------
    contents of the dropbox file : bytes
    """

    _check_dbx()
    metadata, response = dbx.files_download(dropbox_path)
    file_content = response.content
    return file_content


def write_dropbox(dropbox_path, contents):
    _check_dbx()
    """
    write_dropbox
    
    write from dopbox at given path
    
    Parameters
    ----------
    dropbox_path : str or Pathlib.Path
        path to write to

    contents : bytes
        contents to be written
        
    """
    dbx.files_upload(contents, dropbox_path, mode=dropbox.files.WriteMode.overwrite)


def list_local(path):
    path = Path(path)
    return list(path.iterdir())


def write_local(path, contents):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(contents)


def read_local(path):
    path = Path(path)
    with open(path, "rb") as f:
        contents = f.read()
    return contents


class block:
    """
    block is 2 dimensional with 1 as lowest index (like xlwings range) data structure

    Parameters
    ----------
    number_of_rows : int
        number of rows

    number_of_columns : int
        number of columns

    Returns
    -------
    block
    """

    def __init__(self, number_of_rows, number_of_columns):
        self.dict = {}
        self.number_of_columns = number_of_columns
        self.number_of_rows = number_of_rows

    @classmethod
    def from_list_of_lists(cls, list_of_lists, column_like=False):
        """
        from_list_of_lists

        Parameters
        ----------
        list_of_lists : list of lists
            to be used to fill the block

        columns_like : bool
            if False (default), one dimenional lists will be treated as a 1 high range (row-like)

            if True, one dimenional lists will be treated as a 1 wide range (column-like)

            This parameter is not used for proper 2 dimensional list of lists

        Returns
        -------
        block

        Note
        ----
        number_of_rows and number_of_columns will be retrieved from list_of_lists dimension
        """
        if not isinstance(list_of_lists, list):
            list_of_lists = [[list_of_lists]]
        if not isinstance(list_of_lists[0], list):
            if column_like:
                list_of_lists = [[value] for value in list_of_lists]
            else:
                list_of_lists = [list_of_lists]

        self = cls(1, 1)

        self.number_of_rows = len(list_of_lists)
        self._number_of_columns = 0

        for row, row_contents in enumerate(list_of_lists, 1):
            for column, value in enumerate(row_contents, 1):
                if value is not None:
                    self.dict[row, column] = value
                    self._number_of_columns = max(self.number_of_columns, column)
        return self

    def __setitem__(self, row_column, value):
        row, column = row_column
        if row < 1 or row > self.number_of_rows:
            raise IndexError
        if column < 1 or column > self.number_of_columns:
            raise IndexError
        self.dict[row, column] = value

    def __getitem__(self, row_column):
        row, column = row_column
        if row < 1 or row > self.number_of_rows:
            raise IndexError
        if column < 1 or column > self.number_of_columns:
            raise IndexError
        return self.dict.get((row, column))

    @property
    def as_list_of_lists(self):
        return [[self.dict.get((row, column)) for column in range(1, self.number_of_columns + 1)] for row in range(1, self.number_of_rows + 1)]

    @property
    def as_minimal_list_of_lists(self):
        return [[self.dict.get((row, column)) for column in range(1, self.maximum_column + 1)] for row in range(1, self.maximum_row + 1)]

    @property
    def number_of_rows(self):
        return self._number_of_rows

    @number_of_rows.setter
    def number_of_rows(self, value):
        if value<1:
            raise ValueError(f"number_of_rows should be >=1, not {value}")
        self._number_of_rows = value
        for row, column in list(self.dict):
            if row > self._number_of_rows:
                del self.dict[row, column]

    @property
    def number_of_columns(self):
        return self._number_of_columns

    @number_of_columns.setter
    def number_of_columns(self, value):
        if value<1:
            raise ValueError(f"number_of_columns should be >=1, not {value}")
        self._number_of_columns = value
        for row, column in list(self.dict):
            if column > self._number_of_columns:
                del self.dict[row, column]

    @property
    def maximum_row(self):
        if self.dict:
            return max(row for (row, column) in self.dict)
        else:
            return 1

    @property
    def maximum_column(self):
        if self.dict:
            return max(column for (row, column) in self.dict)
        else:
            return 1

    def __repr__(self):
        return f"block.from_list_of_lists({self.as_list_of_lists})"


def clear_captured_stdout():
    """
    empties the captured stdout
    """
    _captured_stdout.clear()


def captured_stdout_as_str():
    """
    returns the captured stdout as a list of strings

    Returns
    -------
    captured stdout : list
        each line is an element of the list
    """

    return "".join(_captured_stdout)


def captured_stdout_as_list_of_lists():
    """
    returns the captured stdout as a list of lists

    Returns
    -------
    captured stdout : list
        each line is an element of the list
    """

    return [[line] for line in captured_stdout_as_str().splitlines()]


class capture_stdout:
    """
    specifies how to capture stdout

    Parameters
    ----------
    include_print : bool
        if True (default), the output is also printed out as normal

        if False, no output is printed

    Note
    ----
    This function is normally used as a context manager, like ::

        with capture_stdout():
            ...
    """

    def __init__(self, include_print: bool = True):
        self.stdout = sys.stdout
        self.include_print = include_print

    def __enter__(self):
        sys.stdout = self

    def __exit__(self, exc_type, exc_value, tb):
        sys.stdout = self.stdout

    def write(self, data):
        _captured_stdout.append(data)
        if self.include_print:
            self.stdout.write(data)

    def flush(self):
        if self.include_print:
            self.stdout.flush()
        _captured_stdout.append("\n")


if __name__ == "__main__":
    ...
