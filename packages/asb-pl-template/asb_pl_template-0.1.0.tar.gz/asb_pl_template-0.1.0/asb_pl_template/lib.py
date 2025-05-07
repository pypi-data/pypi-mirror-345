# asb-pl-template/utils.py
import os
import shutil

def check_directory_exists(path):
    if os.path.exists(path) and os.path.isdir(path):
        return True
    return False


def copy_file(source, destination):
    try:
        shutil.copy2(source, destination)
    except Exception as e:
        print(f"Error copying file: {e}")
