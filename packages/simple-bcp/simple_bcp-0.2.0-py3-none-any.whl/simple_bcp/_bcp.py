import enum
import logging
import os
import pathlib
import shlex
import shutil
import subprocess
import sys
from datetime import timezone, datetime
from typing import Annotated

import packaging.version
from annotated_types import Gt
from pydantic import BaseModel, StringConstraints, Field

_POSITIVE_INT = Annotated[int, Gt(0)]


class MsSqlDatabaseParameters(BaseModel):
    server_hostname: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    port: Annotated[int, Field(gt=0, lt=2 ** 16)] = 1433
    username: str
    password: str
    trust_server_certificate: bool = False


class _Mode(enum.Enum):
    IN = "in"
    OUT = "out"
    QUERY_OUT = "queryout"
    FORMAT = "format"


class BCP:
    def __init__(self, *, bcp_executable_path: pathlib.Path | str | None = None):
        self._init_logger()
        self._init_executable_path(executable_path=bcp_executable_path)
        self._init_bcp_version()

    def _init_logger(self):
        self._logger = logging.getLogger(self.__class__.__name__)

    def _init_executable_path(self, *, executable_path: pathlib.Path | str | None):
        if executable_path is None:
            default = shutil.which("bcp")
            if default is None:
                raise FileNotFoundError(
                    "bcp not found in PATH. Add bcp to PATH environment variable or provide bcp_executable_path explicitly")
            executable_path = pathlib.Path(default)
        elif isinstance(executable_path, str):
            executable_path = pathlib.Path(executable_path)

        if not executable_path.exists():
            raise FileNotFoundError(f"{executable_path.as_posix()} not found")

        if not executable_path.is_file():
            raise OSError(f"path {executable_path} is not a file")

        self._executable_path = executable_path

    def _init_bcp_version(self):
        result = self._run_bcp_command(["-v"])
        # `bcp -v` output example:
        # BCP Utility for Microsoft SQL Server
        # Copyright (C) Microsoft Corporation. All rights reserved.
        # Version 15.0.2000.5
        raw_version = result.strip().split()[-1]
        self._bcp_version = packaging.version.parse(raw_version)
        self._logger.debug(f"BCP version: {self._bcp_version}", extra={"bcp_version": str(self._bcp_version)})

    def _run_bcp_command(self, command_args: list[str]) -> str:
        command = [self._executable_path.as_posix()] + command_args
        self._logger.debug(f"Running command: `{command}`", extra={"bcp_command": shlex.join(command)})
        return subprocess.run(command, capture_output=True, check=True).stdout.decode()

    def _resolve_output_file_path(self, *, path: pathlib.Path | str | None,
                                  default_filename: str) -> pathlib.Path:
        if path is None:
            path = pathlib.Path(os.getcwd()) / default_filename

        if isinstance(path, str):
            path = pathlib.Path(path)

        if path.exists():
            raise FileExistsError(
                f"{path} already exists, bcp requires path to a file that does not exist - and will create it by itself")

        directory_path = path.absolute().parent
        if not directory_path.exists():
            raise FileNotFoundError(f"directory {directory_path} does not exist")

        return path

    def _build_command_args(self, *,
                            mode: _Mode,
                            source_target_specification: str,
                            file_path: pathlib.Path,
                            database_parameters: MsSqlDatabaseParameters,
                            options: dict[str, str | None] = None
                            ) -> list[str]:
        if options is None:
            options = {}
        if sys.platform == "linux" and database_parameters.trust_server_certificate:
            options["-u"] = None  # trust server certificate, available only on linux

        command = [
            source_target_specification,
            mode.value,
            file_path.as_posix(),
            "-S", database_parameters.server_hostname,
            "-U", database_parameters.username,
            "-P", database_parameters.password,
        ]

        for key, value in options.items():
            command.append(key)
            if value is not None:
                command.append(value)

        return command

    def _get_options(self, *, use_native_types: bool, batch_size: _POSITIVE_INT | None) -> dict[str, str | None]:
        options = {}
        if use_native_types:
            options["-n"] = None
        if batch_size is not None:
            options["-b"] = str(batch_size)
        return options

    def _download(self, *, source_target_specification: str, database_parameters: MsSqlDatabaseParameters,
                  output_file_path: pathlib.Path | str | None, batch_size: _POSITIVE_INT | None,
                  default_filename_parts: list[str], mode: _Mode) -> pathlib.Path:
        timestamp = datetime.now(tz=timezone.utc).strftime("%Y%m%d%H%M%S%f")
        default_filename = "-".join(["simple_bcp", *default_filename_parts, timestamp])
        output_file_path = self._resolve_output_file_path(path=output_file_path,
                                                          default_filename=default_filename)
        options = self._get_options(use_native_types=True, batch_size=batch_size)
        command_args = self._build_command_args(mode=mode, source_target_specification=source_target_specification,
                                                file_path=output_file_path, database_parameters=database_parameters,
                                                options=options)
        self._run_bcp_command(command_args)
        return output_file_path

    def download_table(self, *, table_name: str, database_parameters: MsSqlDatabaseParameters,
                       output_file_path: pathlib.Path | str | None = None,
                       batch_size: _POSITIVE_INT | None = None) -> pathlib.Path:
        """
        download table data using bcp

        :param table_name: the name of the table to download
        :param database_parameters: connection details about the database
        :param output_file_path: output the data to this path.
                                 Defaults to None which means let this package decide on the path.
                                 Notice: BCP requires the file to not exist, it will be created using the provided path.
        :param batch_size: Specifies the number of rows per batch of downloaded data
        :return: the path of the downloaded file
        """
        return self._download(
            source_target_specification=table_name,
            database_parameters=database_parameters,
            output_file_path=output_file_path,
            batch_size=batch_size,
            default_filename_parts=[self.download_table.__name__, table_name],
            mode=_Mode.OUT
        )

    def download_query(self, *, query: str, database_parameters: MsSqlDatabaseParameters,
                       output_file_path: pathlib.Path | str | None = None,
                       batch_size: _POSITIVE_INT | None = None) -> pathlib.Path:
        """
        download query result data using bcp

        :param query: sql query string.
                      It is highly recommended to ensure that your SQL query is properly sanitized, in order
                      to avoid security risks such as SQL injection.
                      Consider using packages like SQLAlchemy or other parameterized query libraries
                      to build queries safely.
        :param database_parameters: connection details about the database
        :param output_file_path: output the data to this path.
                                 Defaults to None which means let this package decide on the path.
                                 Notice: BCP requires the file to not exist, it will be created using the provided path.
        :param batch_size: Specifies the number of rows per batch of downloaded data
        :return: the path of the downloaded file
        """
        return self._download(
            source_target_specification=query,
            database_parameters=database_parameters,
            output_file_path=output_file_path,
            batch_size=batch_size,
            default_filename_parts=[self.download_query.__name__],
            mode=_Mode.QUERY_OUT
        )

    def upload_into_table(self, *, table_name: str,
                          database_parameters: MsSqlDatabaseParameters,
                          data_file_path: pathlib.Path | str,
                          batch_size: _POSITIVE_INT | None = None):
        if isinstance(data_file_path, str):
            data_file_path = pathlib.Path(data_file_path)
        if not data_file_path.exists():
            raise FileNotFoundError(f"{data_file_path.as_posix()} does not exist")
        if not data_file_path.is_file():
            raise OSError(f"{data_file_path.as_posix()} is not a file")

        options = self._get_options(use_native_types=True, batch_size=batch_size)
        command_args = self._build_command_args(mode=_Mode.IN, source_target_specification=table_name,
                                                file_path=data_file_path, database_parameters=database_parameters,
                                                options=options)
        self._run_bcp_command(command_args)
