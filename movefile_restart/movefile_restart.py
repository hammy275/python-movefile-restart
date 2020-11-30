import sys
import os

if sys.platform != "win32":
    raise OSError("python-movefile-restart module is only supported on Windows systems!")

import winreg

_registry = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
_key = winreg.OpenKey(_registry, "SYSTEM\\CurrentControlSet\\Control\\Session Manager", 0, winreg.KEY_ALL_ACCESS)

def __get_current_values():
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
    winreg.SetValueEx(_key, "PendingFileRenameOperations", 0, winreg.REG_MULTI_SZ, values)


def DeleteFile(file_path):
    file_path = file_path.replace("/", "\\")
    if not (os.path.isfile(file_path)):
        raise FileNotFoundError("Path {} does not exist!".format(file_path))
    values = __get_current_values()
    values.append("\\??\\" + file_path)
    values.append("")
    __set_registry(values)
    

def MoveFile(from_path, to_path):
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
    MoveFile(from_path, to_path)


if __name__ == "__main__":
    DeleteFile("C:\\Users\\hammy3502\\Desktop\\a.txt")
    MoveFile("C:\\Users\\hammy3502\\Desktop\\b.txt", "C:\\Users\\hammy3502\\Desktop\\a.txt")
    print("Currently, there isn't anything implemented for directly running this file.")
    sys.exit()