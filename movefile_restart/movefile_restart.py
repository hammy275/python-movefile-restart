import sys
import os

if sys.platform != "win32":
    raise OSError("movefile-restart module is only supported on Windows systems!")

import winreg

_registry = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
_key = winreg.OpenKey(_registry, "SYSTEM\\CurrentControlSet\\Control\\Session Manager", 0, winreg.KEY_ALL_ACCESS)

def __get_current_values():
    """Get Values.

    Internal function to get the current values stored inside PendingFileRenameOperations as a giant list of strings.

    Returns:
        str[]: List of strings in PendingFileRenameOperations

    """
    file_ops_values = None
    i = 0
    while True:
        try:
            if winreg.EnumValue(_key,i)[0] == "PendingFileRenameOperations":
                file_ops_values = winreg.EnumValue(_key,i)[1]
                break
        except Exception:
            break
        i += 1
    if file_ops_values == None:
        return []
    return file_ops_values


def __set_registry(values):
    """Set PendingFileRenameOperations.

    Use at your own risk internal function. Takes a list of strings, and writes it to PendingFileRenameOperations.

    Args:
        values (str[]): List of strings to write to PendingFileRenameOperations key.

    """
    winreg.SetValueEx(_key, "PendingFileRenameOperations", 0, winreg.REG_MULTI_SZ, values)


def DeleteFile(file_path):
    """Queue File for Deletion.

    Adds the Registry information to delete a file on reboot.

    Args:
        file_path (str): A path to the file to delete.

    Raises:
        FileNotFoundError: Raised if the file_path doesn't exist.

    """
    file_path = file_path.replace("/", "\\")
    if not (os.path.isfile(file_path)):
        raise FileNotFoundError("Path {} does not exist!".format(file_path))
    values = __get_current_values()
    values.append("\\??\\" + file_path)
    values.append("")
    __set_registry(values)
    

def MoveFile(from_path, to_path):
    """Queue File for Moving.

    Adds the Registry information to move a file on reboot.

    Args:
        from_path (str): The directory being moved from.
        to_path (str): The directory being moved to.

    Raises:
        FileNotFoundError: Raised if the from_path doesn't exist or if the directory of to_path doesn't exist.
        FileExistsError: Raised if to_path already exists.

    """
    from_path = from_path.replace("/", "\\")
    if not os.path.isfile(from_path):  # Don't move non-existant path
        raise FileNotFoundError("Path {} does not exist!".format(from_path))
    to_path = to_path.replace("/", "\\")
    if not os.path.isdir(os.path.dirname(to_path)):  # Don't move to non-existant dir
        raise FileNotFoundError("Path {} does not exist to move to!".format(os.path.dirname(to_path)))
    values = __get_current_values()
    if os.path.isfile(to_path):  # Don't move to already-existing destination unless it will be deleted/moved
        values.reverse()
        try:
            to_path_index = values.index("\\??\\" + to_path)
        except ValueError:
            to_path_index = -1
        if to_path_index % 2 == 0 or to_path_index == -1:
            raise FileExistsError("Path {} already exists and isn't already being deleted/moved!".format(to_path))
        values.reverse()
    values.append("\\??\\" + from_path)
    values.append("\\??\\" + to_path)
    __set_registry(values)


def RenameFile(from_path, to_path):
    """MoveFile Alias."""
    MoveFile(from_path, to_path)


def GetFileOperations():
    """Get Pending File Operations.
    
    Returns a list with tuples of the format (from_path, to_path). If to_path is empty, then the file is being deleted.

    Returns:
        tuple[]: A list of tuples containing the pending file operations.

    """
    values = __get_current_values()
    to_return = []
    for i in range(int(len(values) / 2)):
        to_return.append((values[2*i].replace("\\??\\", ""), values[2*i+1].replace("\\??\\", "")))
    return to_return


def PrintFileOperations():
    """Prints Pending File Operations."""
    vals = GetFileOperations()
    for i in vals:
        if i[1] == "":
            print("Deleting {}".format(i[0]))
        else:
            print("Moving {} to {}".format(i[0], i[1]))


if __name__ == "__main__":
    print("Currently pending file operations: ")
    PrintFileOperations()
    sys.exit()