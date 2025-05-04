import enum
import logging
import os
import pathlib
import shlex
import shutil
import subprocess
import sys
from datetime import timezone, datetime
from typing import Annotated, Literal

import packaging.version
from annotated_types import Gt
from pydantic import BaseModel, StringConstraints, Field

from ._encoding import FieldEncodingType, BcpEncodingSettings

_POSITIVE_INT = Annotated[int, Gt(0)]


class MsSqlDatabaseParameters(BaseModel):
    server_hostname: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    port: Annotated[int, Field(gt=0, lt=2 ** 16)] = 1433
    username: str
    password: str
    trust_server_certificate: bool = False
    database_name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)] | None = Field(
        default=None, description="database name. defaults to the user's default database name")


class _BcpMode(enum.Enum):
    IN = "in"
    OUT = "out"
    QUERY_OUT = "queryout"
    FORMAT = "format"


class BCP:
    def __init__(
            self, *,
            bcp_executable_path: pathlib.Path | str | None = None
    ):
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

    def _resolve_output_file_path(
            self, *,
            path: pathlib.Path | str | None,
            default_filename: str,
    ) -> pathlib.Path:
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

    def _build_command_args(
            self, *,
            mode: _BcpMode,
            source_target_specification: str,
            file_path: pathlib.Path,
            database_parameters: MsSqlDatabaseParameters,
            options: dict[str, str | None] = None,
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

        if database_parameters.database_name is not None:
            command.extend(["-d", database_parameters.database_name])

        for key, value in options.items():
            command.append(key)
            if value is not None:
                command.append(value)

        return command

    def _get_options(
            self, *,
            batch_size: _POSITIVE_INT | None,
            bcp_encoding_settings: BcpEncodingSettings | None,
    ) -> dict[str, str | None]:
        if bcp_encoding_settings is None:
            bcp_encoding_settings = BcpEncodingSettings()
        
        if bcp_encoding_settings.field_encoding_type is FieldEncodingType.NATIVE and (
                bcp_encoding_settings.field_delimiter is not None or bcp_encoding_settings.row_terminator is not None):
            raise ValueError("NATIVE field encoding mode cannot be used with field_delimiter or row_terminator")

        # this type hinting is just to avoid (another) weird PyCharm typing bug due to the if statement above
        # https://youtrack.jetbrains.com/issue/PY-80870
        # noinspection PyTypeHints
        bcp_encoding_settings.field_encoding_type: FieldEncodingType
        options: dict[str, str | None] = {
            bcp_encoding_settings.field_encoding_type.value: None
        }
        if batch_size is not None:
            options["-b"] = str(batch_size)
        if bcp_encoding_settings.field_delimiter is not None:
            options["-t"] = bcp_encoding_settings.field_delimiter
        if bcp_encoding_settings.row_terminator is not None:
            options["-r"] = bcp_encoding_settings.row_terminator
        return options

    def _download(
            self, *,
            source_target_specification: str,
            database_parameters: MsSqlDatabaseParameters,
            output_file_path: pathlib.Path | str | None,
            batch_size: _POSITIVE_INT | None,
            default_filename_parts: list[str],
            mode: Literal[_BcpMode.OUT, _BcpMode.QUERY_OUT],
            bcp_encoding_settings: BcpEncodingSettings | None,
    ) -> pathlib.Path:
        timestamp = datetime.now(tz=timezone.utc).strftime("%Y%m%d%H%M%S%f")
        default_filename = "-".join(["simple_bcp", *default_filename_parts, timestamp])
        output_file_path = self._resolve_output_file_path(path=output_file_path,
                                                          default_filename=default_filename)
        options = self._get_options(batch_size=batch_size, bcp_encoding_settings=bcp_encoding_settings)
        command_args = self._build_command_args(mode=mode, source_target_specification=source_target_specification,
                                                file_path=output_file_path, database_parameters=database_parameters,
                                                options=options)
        self._run_bcp_command(command_args)
        return output_file_path

    def download_table(
            self, *,
            table_name: str,
            database_parameters: MsSqlDatabaseParameters,
            output_file_path: pathlib.Path | str | None = None,
            batch_size: _POSITIVE_INT | None = None,
            bcp_encoding_settings: BcpEncodingSettings | None = None,
    ) -> pathlib.Path:
        """
        download table data using bcp

        :param table_name: The name of the table to download.
           May be of one of 2 formats - either simply `table_name` or `database_name.schema.table_name`.
           If `database_name.schema.table_name` is used and `database_parameters.database_name` is set to a different
           database, bcp may have an error and a `subprocess.CalledProcessError` may be raised.
        :param database_parameters: database connection details
        :param output_file_path: output the data to this path.
                                 Defaults to None which means let this package decide on the path.
                                 Notice: BCP requires the file to not exist, it will be created using the provided path.
        :param batch_size: Specifies the number of rows per batch of downloaded data
        :param bcp_encoding_settings: how to encode the downloaded data. defaults to `EncodingOptions()`
        :return: the path of the downloaded file
        """
        return self._download(
            source_target_specification=table_name,
            database_parameters=database_parameters,
            output_file_path=output_file_path,
            batch_size=batch_size,
            default_filename_parts=[self.download_table.__name__, table_name],
            mode=_BcpMode.OUT,
            bcp_encoding_settings=bcp_encoding_settings,
        )

    def download_query(
            self, *,
            query: str,
            database_parameters: MsSqlDatabaseParameters,
            output_file_path: pathlib.Path | str | None = None,
            batch_size: _POSITIVE_INT | None = None,
            bcp_encoding_settings: BcpEncodingSettings | None = None,
    ) -> pathlib.Path:
        """
        download query result data using bcp

        :param query: sql query string.
          It is highly recommended to ensure that your SQL query is properly sanitized, in order to avoid security risks
          such as SQL injection.
          Consider using packages like SQLAlchemy or other parameterized query libraries to build queries safely.
          Table and views names in your query may be of one of 2 formats - either simply `table_name` or
          `database_name.schema.table_name`.
          If `database_name.schema.table_name` is used and `database_parameters.database_name` is set to a different
          database, bcp may have an error and a `subprocess.CalledProcessError` may be raised.

        :param database_parameters: database connection details
        :param output_file_path: output the data to this path.
                                 Defaults to None which means let this package decide on the path.
                                 Notice: BCP requires the file to not exist, it will be created using the provided path.
        :param batch_size: Specifies the number of rows per batch of downloaded data
        :param bcp_encoding_settings: how to encode the downloaded data. defaults to `EncodingOptions()`
        :return: the path of the downloaded file
        """
        return self._download(
            source_target_specification=query,
            database_parameters=database_parameters,
            output_file_path=output_file_path,
            batch_size=batch_size,
            default_filename_parts=[self.download_query.__name__],
            mode=_BcpMode.QUERY_OUT,
            bcp_encoding_settings=bcp_encoding_settings,

        )

    def upload_into_table(
            self, *,
            table_name: str,
            database_parameters: MsSqlDatabaseParameters,
            data_file_path: pathlib.Path | str,
            batch_size: _POSITIVE_INT | None = None,
            bcp_encoding_settings: BcpEncodingSettings | None = None,
    ) -> None:
        """
        Upload data created by bcp (`download_query` or `download_table`) - into a table.
        :param table_name: The name of the table to upload to.
           May be of one of 2 formats - either simply `table_name` or `database_name.schema.table_name`.
           If `database_name.schema.table_name` is used and `database_parameters.database_name` is set to a different
           database, bcp may have an error and a `subprocess.CalledProcessError` may be raised.
        :param database_parameters: database connection details
        :param data_file_path: the path of the data to upload
        :param batch_size: Specifies the number of rows per batch of uploaded data
        :param bcp_encoding_settings: how to encode the downloaded data. defaults to `EncodingOptions()`
        """
        if isinstance(data_file_path, str):
            data_file_path = pathlib.Path(data_file_path)
        if not data_file_path.exists():
            raise FileNotFoundError(f"{data_file_path.as_posix()} does not exist")
        if not data_file_path.is_file():
            raise OSError(f"{data_file_path.as_posix()} is not a file")

        options = self._get_options(bcp_encoding_settings=bcp_encoding_settings, batch_size=batch_size)
        command_args = self._build_command_args(mode=_BcpMode.IN, source_target_specification=table_name,
                                                file_path=data_file_path, database_parameters=database_parameters,
                                                options=options)
        self._run_bcp_command(command_args)
