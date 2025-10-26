import shutil
import kagglehub
import pandas as pd
import os
import requests
import zipfile


def unzip_file(zip_path, extract_dir=None):
    """
    Unzips a ZIP file to a specified directory.

    Parameters
    ----------
    zip_path : str
        Path to the .zip file.
    extract_dir : str, optional
        Directory to extract files to.
        Defaults to a folder with the same name as the zip file.

    Returns
    -------
    str
        Path to the directory where files were extracted.

    Raises
    ------
    FileNotFoundError
        If the zip file does not exist.
    ValueError
        If the provided file is not a .zip file.
    """
    # Check file validity
    if not os.path.isfile(zip_path):
        raise FileNotFoundError(f"No file found at: {zip_path}")

    if not zip_path.lower().endswith(".zip"):
        raise ValueError(f"File is not a ZIP archive: {zip_path}")

    # Default extraction directory
    if extract_dir is None:
        extract_dir = os.path.splitext(zip_path)[0]  # same name as the zip file

    os.makedirs(extract_dir, exist_ok=True)

    # Extract files
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)

    print(f"✅ Extracted '{zip_path}' → '{extract_dir}'")

    return extract_dir


def move_to_project(src_path, target_dir, filename=None):
    """
    Move a file from a source path (file or directory) to a target directory.
    Searches recursively if the source is a directory.
    If filename is specified, move that file; otherwise, move the first file found.

    Parameters
    ----------
    src_path : str
        Path to a file or directory containing file(s).
    target_dir : str
        Path to the target directory.
    filename : str, optional
        Specific filename to move. If not provided, the first file found is moved.

    Returns
    -------
    str
        Path to the moved file.

    Raises
    ------
    FileNotFoundError
        If the source file/directory does not exist, or if the specified filename is not found.
    """
    if not os.path.exists(src_path):
        raise FileNotFoundError(f"Source path not found: {src_path}")

    # If src_path is a single file
    if os.path.isfile(src_path):
        src_file = src_path
        if filename and os.path.basename(src_file) != filename:
            raise FileNotFoundError(f"Specified file '{filename}' not found at {src_path}")
    else:
        # src_path is a directory → walk recursively
        found_file = None
        for root, dirs, files in os.walk(src_path):
            if filename:
                if filename in files:
                    found_file = os.path.join(root, filename)
                    break
            else:
                if files:
                    found_file = os.path.join(root, files[0])
                    break

        if not found_file:
            if filename:
                raise FileNotFoundError(f"File '{filename}' not found under {src_path}")
            else:
                raise FileNotFoundError(f"No files found under {src_path}")
        src_file = found_file

    # Ensure target directory exists
    os.makedirs(target_dir, exist_ok=True)
    dest_file = os.path.join(target_dir, os.path.basename(src_file))

    shutil.copy(src_file, dest_file)
    print(f"✅ Moved '{src_file}' → '{dest_file}'")
    return dest_file


def file_to_df(file_path):
    """
    Read a CSV or Excel file into a pandas DataFrame.
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".csv":
        return pd.read_csv(file_path)
    elif ext in [".xls", ".xlsx"]:
        return pd.read_excel(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def read_kaggle_dataset(url, target=os.path.join(os.getcwd(), "data"), filename=None):
    """
    Take a URL ("url") of a Kaggle dataset, download the csv into its own folder (specified by "target") in the
    project, and read it into a Pandas DataFrame.

    Parameters
    ---------
    url: str
        The URL of the Kaggle dataset
    target: str, optional
        Path within project directory to store downloaded csv (default is "data")
    filename: str, optional
        Name of the specific file to read from the dataset. If none is provided, the first file found will be picked

    Returns
    ------
    pandas.DataFrame
        The dataframe containing the csv contents.
    """
    path = kagglehub.dataset_download(url)
    dest_file = move_to_project(path, target, filename=filename)
    print(f"Downloaded and read {dest_file}")
    return file_to_df(dest_file)
