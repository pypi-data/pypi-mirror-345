# vim: set tabstop=4 expandtab :
###############################################################################
#   Copyright (c) 2024 Thomas Winkler <thomas.winkler@gmail.com>
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
###############################################################################

import subprocess
import os
import sys
import platform
from pathlib import Path


class DottRuntime:
    IDENTIFIER: str | None = None
    VERSION: str | None = None
    GDBPATH: str | None = None
    GDBCLIENT: str | None = None
    PYTHON_EMB_PATH: str | None = None
    PYTHON_EMB_PACKAGEPATH: str | None = None
    RUNTIMEPATH: str | None = None

    @staticmethod
    def setup_runtime() -> None:
        dott_runtime_path = sys.prefix + os.sep + 'dott_data'
        if os.path.exists(dott_runtime_path):
            runtime_version: str = 'unknown'
            with Path(dott_runtime_path + '/apps/version.txt').open() as f:
                line = f.readline()
                while line:
                    if 'version:' in line:
                        runtime_version = line.lstrip('version:').strip()
                        break
                    line = f.readline()
            DottRuntime.RUNTIMEPATH = dott_runtime_path
            DottRuntime.IDENTIFIER = f'{dott_runtime_path} (dott-runtime package)'
            DottRuntime.VERSION = runtime_version
            DottRuntime.GDBPATH = str(Path(f'{dott_runtime_path}/apps/gdb/bin'))
            DottRuntime._set_exec_paths()

            # Linux: check if required libraries are installed. Windows: They are included in the DOTT runtime.
            if platform.system() == 'Linux':
                my_env = os.environ
                ld_lib_path = f'{os.pathsep}{my_env["LD_LIBRARY_PATH"]}' if 'LD_LIBRARY_PATH' in my_env.keys() else ''
                os.environ['LD_LIBRARY_PATH'] = f'{DottRuntime.PYTHON_EMB_PATH}{ld_lib_path}'
                res = subprocess.run([DottRuntime.GDBCLIENT, '--version'], stdout=subprocess.PIPE)
                if res.returncode != 0:
                    raise RuntimeError('Unable to start gdb client. This might be caused by missing dependencies.\n'
                                       'Make sure that libdl, librt, libpthread, libutil and libncurses6 are installed.')

    @staticmethod
    def _set_exec_paths() -> None:
        match DottRuntime.VERSION:
            case '1.1.1' | '1.1.2':
                if platform.system() == 'Linux':
                    DottRuntime.PYTHON_EMB_PATH = ''  # The 1.1.x Linux RT assumes Python 2.7 is available on the host.
                    DottRuntime.GDBCLIENT = f'{DottRuntime.GDBPATH}/arm-none-eabi-gdb-py'
                    DottRuntime.PYTHON_EMB_PACKAGEPATH = ''
                else:
                    DottRuntime.PYTHON_EMB_PATH = str(Path(f'{DottRuntime.RUNTIMEPATH}/apps/python27/python-2.7.13'))
                    DottRuntime.GDBCLIENT = f'{DottRuntime.GDBPATH}/arm-none-eabi-gdb-py.exe'
                    DottRuntime.PYTHON_EMB_PACKAGEPATH = str(Path(f'{DottRuntime.PYTHON_EMB_PATH}/Lib'))

            case '2.13.3' | _:
                # "new-style" is also the current default
                if platform.system() == 'Linux':
                    DottRuntime.PYTHON_EMB_PATH = str(Path(f'{DottRuntime.RUNTIMEPATH}/apps/python_embedded/lib'))
                    DottRuntime.GDBCLIENT = f'{DottRuntime.GDBPATH}/arm-none-eabi-gdb'
                    DottRuntime.PYTHON_EMB_PACKAGEPATH = str(Path(f'{DottRuntime.PYTHON_EMB_PATH}/python3.12'))
                else:
                    DottRuntime.PYTHON_EMB_PATH = str(Path(f'{DottRuntime.RUNTIMEPATH}/apps/python_embedded'))
                    DottRuntime.GDBCLIENT = f'{DottRuntime.GDBPATH}/arm-none-eabi-gdb.exe'
                    DottRuntime.PYTHON_EMB_PACKAGEPATH = str(Path(f'{DottRuntime.PYTHON_EMB_PATH}/Lib'))

        os.environ['PYTHONHOME'] = DottRuntime.PYTHON_EMB_PATH.rstrip('lib')

    @staticmethod
    def dump():
        val: str = (f'IDENTIFIER: {DottRuntime.IDENTIFIER}{os.linesep}'
                    f'VERSION: {DottRuntime.VERSION}{os.linesep}'
                    f'GDBPATH: {DottRuntime.GDBPATH}{os.linesep}'
                    f'GDBCLIENT: {DottRuntime.GDBCLIENT}{os.linesep}'
                    f'PYTHON_EMB_PATH: {DottRuntime.PYTHON_EMB_PATH}{os.linesep}'
                    f'PYTHON_EMB_PACKAGEPATH: {DottRuntime.PYTHON_EMB_PACKAGEPATH}{os.linesep}'
                    f'RUNTIMEPATH: {DottRuntime.RUNTIMEPATH}{os.linesep}')
        return val
