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


def move_to_project(src_dir, target_dir, filename=None):
    """
    Move a file from a source directory to a target directory.
    If filename is specified, move that file; otherwise, move the first file in the directory.

    Parameters
    ----------
    src_dir : str
        Path to the source directory containing the file(s).
    target_dir : str
        Path to the target directory.
    filename : str, optional
        Specific filename to move. If not provided, the first file is moved.

    Returns
    -------
    str
        Path to the moved file.

    Raises
    ------
    FileNotFoundError
        If the source directory does not exist or the specified file is not found.
    """
    if not os.path.isdir(src_dir):
        raise FileNotFoundError(f"Source directory not found: {src_dir}")

    files = os.listdir(src_dir)
    if not files:
        raise FileNotFoundError(f"No files found in source directory: {src_dir}")

    # Determine which file to move
    if filename:
        if filename not in files:
            raise FileNotFoundError(f"Specified file '{filename}' not found in source directory")
        selected_file = filename
    else:
        selected_file = files[0]

    src_file = os.path.join(src_dir, selected_file)
    os.makedirs(target_dir, exist_ok=True)
    dest_file = os.path.join(target_dir, selected_file)

    shutil.copy(src_file, dest_file)
    return dest_file


def csv_to_df(path_or_url, download_dir="data"):
    """
    Load a CSV file into a pandas DataFrame.
    If a URL is provided, downloads the file locally first.

    Parameters
    ----------
    path_or_url : str
        The file path or URL to a CSV file.
    download_dir : str, optional
        Directory to store downloaded files (default is "data").

    Returns
    -------
    pandas.DataFrame
        The loaded DataFrame.
    """
    # If input is a URL
    if isinstance(path_or_url, str) and path_or_url.startswith(("http://", "https://")):
        # Make sure the download directory exists
        os.makedirs(download_dir, exist_ok=True)

        # Extract filename from URL
        filename = os.path.basename(path_or_url.split("?")[0])  # remove query strings if present
        local_path = os.path.join(download_dir, filename)

        # Download the file
        try:
            response = requests.get(path_or_url)
            response.raise_for_status()  # raise an error for bad responses
            with open(local_path, "wb") as f:
                f.write(response.content)
            print(f"Downloaded CSV to: {local_path}")
        except Exception as e:
            raise ValueError(f"Failed to download CSV from URL: {e}")

        # Read CSV into DataFrame
        df = pd.read_csv(local_path)

    # If input is a local file
    elif os.path.isfile(path_or_url):
        df = pd.read_csv(path_or_url)

    else:
        raise ValueError("Input must be a valid CSV file path or URL.")

    return df


def read_kaggle_dataset(url, target=os.path.join(os.getcwd(), "data")):
    """
    Take a URL ("url") of a Kaggle dataset, download the csv into its own folder (specified by "target") in the
    project, and read it into a Pandas DataFrame.

    Parameters
    ---------
    url: str
        The URL of the Kaggle dataset
    target: str, optional
        Path within project directory to store downloaded csv (default is "data")

    Returns
    ------
    pandas.DataFrame
        The dataframe containing the csv contents.
    """
    path = kagglehub.dataset_download(url)
    dest_file = move_to_project(path, target)
    print(f"Downloaded and read {dest_file}")
    return csv_to_df(dest_file)
