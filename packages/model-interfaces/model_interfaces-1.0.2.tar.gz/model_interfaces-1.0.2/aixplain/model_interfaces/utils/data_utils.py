import logging
import time
import requests
from pathlib import Path


def download_external_data(url_link, root_dir: Path = None):
    local_filename = url_link.split("/")[-1]
    if root_dir is not None:
        local_filename = root_dir / local_filename
        local_filename = str(local_filename.resolve())
    with requests.get(url_link, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                # if chunk:
                f.write(chunk)
    return local_filename


def download_data(data_url, root_dir: Path = None):
    start = time.time()
    try:
        path = download_external_data(data_url, root_dir)
    except:
        raise Exception(f"Input data {data_url} not found")
    end = time.time()
    logging.info(f"Downloading {data_url} - Time in Seconds: {str(round(end-start, 2))}")
    return path
