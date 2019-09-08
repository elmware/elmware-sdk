# -*- coding: utf-8 -
#
import requests
from requests.packages.urllib3.exceptions import HTTPError
from requests.exceptions import ConnectionError
from .base_functions import ElmwareError


class ElmwareStorageError(ElmwareError):
    pass


class StoreFile:
    @classmethod
    def store_file(cls, upload_url, file_path):
        """
        method for uploading files from container to storage
        """
        files = False
        outcome = False
        try:
            with open(file_path, "rb") as data:
                headers = {}
                if ("windows" in upload_url) or ("azure" in upload_url):
                    headers["x-ms-blob-type"] = "BlockBlob"
                    files = {"file": data}
                if files:
                    req = requests.put(upload_url, files=files, headers=headers)
                else:
                    # legacy non-multi part for s3 upload
                    req = requests.put(upload_url, data=data, headers=headers)
                if str(req.status_code)[0] == "2":
                    outcome = True
        except FileNotFoundError:
            raise ElmwareStorageError("Invalid File Path")
        except (HTTPError, ConnectionError):
            raise ElmwareStorageError("Unable to Connect to file server")
        if not outcome:
            raise ElmwareStorageError("Failed to store file.")
        return True
