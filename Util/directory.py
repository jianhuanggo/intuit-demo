from os import walk, umask, makedirs, path
import shutil


def createdirectory(dirpath: str) -> bool:
    """
    Creates the directory specified by path, creating intermediate directories
    as necessary. If directory already exists, this is a no-op.
    :param dirpath: The directory to create

    :param logger: The directory to create
    :type : str
    """
    try:
        o_umask = umask(0)
        makedirs(dirpath)
    except FileExistsError:
        return True
    except OSError:
        if not path.isdir(dirpath):
            raise OSError
    except Exception as err:
        raise err
    else:
        print(f"Successfully created the directory {dirpath}")
        return True
    finally:
        umask(o_umask)
    return True


def remove_directory(filepath: str) -> bool:
    try:
        shutil.rmtree(filepath)
        return True
    except Exception as err:
        print(err)
        return False


def is_dir_exist(filepath: str) -> bool:
    return path.isdir(filepath)


def files_in_dir(filepath: str) :
    try:
        _, _, filenames = next(walk(filepath))
        return filenames

    except Exception as err:
        raise err

