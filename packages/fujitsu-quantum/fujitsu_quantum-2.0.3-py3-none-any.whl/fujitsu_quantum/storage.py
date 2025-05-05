# (C) 2024 Fujitsu Limited

import io
import json
import os.path
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from http import HTTPStatus
from io import BytesIO
from os import PathLike
from pathlib import Path
from typing import Any, Union
from zipfile import ZipFile

from fujitsu_quantum import logging
from fujitsu_quantum.config import Config
from fujitsu_quantum.requests import FQCRequest, Request, RequestError
from fujitsu_quantum.types import single_to_multiple_values, to_api_operator, to_sdk_operator


@dataclass
class ObjectReference:
    """A reference to an object uploaded to Quantum Cloud."""
    key: str


class StorageObjectDownloadError(Exception):
    """
    Attributes:
        url: storage object URL
        message: error message.
    """

    def __init__(self, url: str, message: str):
        super().__init__(url, message)
        self.url = url
        self.message = message

    def __str__(self):
        return f'{self.message}. URL: {self.url}'


class StorageService:

    ENDPOINT: str = Config.api_base + '/tasks'

    _OBJECT_EXT: str = ".zip"

    @staticmethod
    def upload(items: dict[str, dict[str, Any]], overwrite: bool = False) -> dict[str, ObjectReference]:
        """Uploads parameter values to the object storage.

        Args:
            items (dict[str, dict[str, Any]]): a dict of key and parameter-values pairs. The parameter-values is a dict
                                               of parameter name and value pairs.
            overwrite (bool): whether to overwrite existing objects having the same keys in the storage.

        Returns:
            dict[str, ObjectReference]: a dict of key and ObjectReference pairs.
        """
        register_files_request_body = {
            "mode": "register_task_files",
            "overwrite": overwrite,
            "files": [key + StorageService._OBJECT_EXT for key in items.keys()]
        }

        upload_params = FQCRequest.post(status_code=HTTPStatus.OK, url=StorageService.ENDPOINT,
                                        data=json.dumps(register_files_request_body)).json()

        # TODO parallel uploads for better performance
        result = {}
        for key, upload_param in zip(items, upload_params):
            with io.BytesIO() as zip_buffer:
                zip_buffer.name = key + StorageService._OBJECT_EXT
                with ZipFile(file=zip_buffer, mode="w") as zip_arch:
                    # Before uploading parameter values, we convert them such that their values satisfy the followings.
                    # - single values are not used (e.g., type(code) is always list)
                    # - "operator" values are in the Web API format.
                    param_values, converted_param_names = single_to_multiple_values(items[key])
                    for param, value in param_values.items():
                        if param == 'operator':
                            value = to_api_operator(value)
                        zip_arch.writestr(zinfo_or_arcname=f'{param}.json', data=json.dumps(value))

                    zip_arch.writestr(zinfo_or_arcname='metadata.json',
                                      data=json.dumps({'sdkSingleValueParams': converted_param_names}))

                zip_buffer.seek(0)
                Request.post(exp_status_code=HTTPStatus.NO_CONTENT,
                             url=upload_param['url'],
                             data=upload_param['fields'],
                             files={'file': (os.path.basename(zip_buffer.name), zip_buffer, 'application/zip')})

            result[key] = ObjectReference(key)

        return result

    @staticmethod
    def _download(url_or_path: str, use_local_storage: bool) -> dict[str, Any]:

        with io.BytesIO() as zip_buffer:
            if use_local_storage:
                with open(url_or_path, 'rb') as f:
                    zip_buffer.write(f.read())
            else:
                resp = Request.get(url=url_or_path)
                zip_buffer.write(resp.content)

            zip_buffer.flush()
            zip_buffer.seek(0)
            try:
                result = StorageService._extract_zip_object(zip_buffer)
            except Exception as e:
                log_file_path = StorageService._write_error_log(f'The storage object is corrupted. Path: {url_or_path}.\n'
                                                                f'Error details: {type(e)}. {e}')
                raise StorageObjectDownloadError(url_or_path, f'The storage object is corrupted.'
                                                                f' Error details have been saved to {log_file_path}')

        return result

    @staticmethod
    def _extract_zip_object(zip_buffer: BytesIO):
        result = {}
        with ZipFile(zip_buffer, 'r') as zip_arch:
            json_file_path_list = zip_arch.namelist()
            for json_file_path in json_file_path_list:
                param_name = Path(json_file_path).stem
                with zip_arch.open(json_file_path) as json_file:
                    value = json.loads(json_file.read())
                    if param_name == 'operator':
                        value = to_sdk_operator(value)
                    result[param_name] = value

        metadata = result.pop('metadata', None)
        if metadata is not None:
            for param_name in metadata['sdkSingleValueParams']:
                result[param_name] = result[param_name][0]

        return result

    @staticmethod
    def _write_error_log(err_msg: str):
        err_msg_header = f'StorageFileError occurred at {str(datetime.now(timezone.utc))} UTC.\n----------------------------\n'
        return logging.write_error_log(f'{err_msg_header}{err_msg}')

    @staticmethod
    def _upload_hybrid_program(key: str, zip_buffer: BytesIO, overwrite: bool = False):
        register_files_request_body = {
            "mode": "register_task_files",
            "overwrite": overwrite,
            "files": [key + StorageService._OBJECT_EXT]
        }

        upload_param = FQCRequest.post(status_code=HTTPStatus.OK, url=StorageService.ENDPOINT,
                                       data=json.dumps(register_files_request_body)).json()[0]

        zip_file_name = os.path.basename(key) + StorageService._OBJECT_EXT
        Request.post(exp_status_code=HTTPStatus.NO_CONTENT,
                     url=upload_param['url'],
                     data=upload_param['fields'],
                     files={'file': (zip_file_name, zip_buffer, 'application/zip')})

    @staticmethod
    def _download_hybrid_program_result(object_url: str, save_dir: Union[str, PathLike],
                                        get_fresh_object_url: Callable[[], str]):
        try:
            # TODO suppress the error log file output when the url is expired (403 error)
            resp = Request.get(url=object_url)
        except RequestError:
            # Since the pre-signed URL can be expired, obtain a new pre-signed URL to download the result data
            resp = Request.get(url=get_fresh_object_url())

        Path(save_dir).mkdir(parents=True, exist_ok=True)
        with ZipFile(BytesIO(resp.content)) as zip_arch:
            zip_arch.extractall(path=save_dir)
