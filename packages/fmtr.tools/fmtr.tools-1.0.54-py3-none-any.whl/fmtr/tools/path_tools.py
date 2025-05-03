import re
import subprocess
from inspect import stack
from pathlib import Path
from tempfile import gettempdir
from typing import Union, Any

from fmtr.tools.config import ToolsConfig
from fmtr.tools.platform_tools import is_wsl

WIN_PATH_PATTERN = r'''([a-z]:(\\|$)|\\\\)'''
WIN_PATH_RX = re.compile(WIN_PATH_PATTERN, flags=re.IGNORECASE)


class WSLPathConversionError(EnvironmentError):
    """

    Error to raise if WSL path conversion fails.

    """


class Path(type(Path())):
    """

    Custom path object aware of WSL paths, with some additional read/write methods

    """

    def __new__(cls, *segments: Union[str, Path], convert_wsl: bool = True, **kwargs):
        """

        Intercept arguments to detect whether WSL conversion is required.

        """
        if convert_wsl and len(segments) == 1 and is_wsl() and cls.is_abs_win_path(*segments):
            segments = [cls.from_wsl(*segments)]

        return super().__new__(cls, *segments, **kwargs)

    @classmethod
    def is_abs_win_path(cls, path: Union[str, Path]) -> bool:
        """

        Infer if the current path is an absolute Windows path.

        """
        path = str(path)
        return bool(WIN_PATH_RX.match(path))

    @classmethod
    def from_wsl(cls, path: Union[str, Path]) -> bool:  # pragma: no cover
        """

        Call `wslpath` to convert the path to its Unix equivalent.

        """
        result = subprocess.run(['wslpath', '-u', str(path)], capture_output=True, text=True)

        if result.returncode:
            msg = f'Could not convert Windows path to Unix equivalent: "{path}"'
            raise WSLPathConversionError(msg)

        path_wsl = result.stdout.strip()
        path_wsl = cls(path_wsl, convert_wsl=False)
        return path_wsl

    @classmethod
    def package(cls) -> 'Path':
        """

        Get path to originating module (e.g. directory containing .py file).

        """
        frame_called = stack()[1]
        path = cls(frame_called.filename).absolute().parent
        return path

    @classmethod
    def module(cls) -> 'Path':
        """

        Get path to originating module (i.e. .py file).

        """
        frame_called = stack()[1]
        path = cls(frame_called.filename).absolute()
        return path

    @classmethod
    def temp(cls) -> 'Path':
        """

        Get path to temporary directory.

        """
        return cls(gettempdir())

    @classmethod
    def data(cls, name='data') -> 'Path':
        """

        Fetch canonical "data"/"artifacts" path, whether calling package is regular or namespace package.

        """
        from fmtr.tools.inspection_tools import get_call_path
        path = get_call_path()
        path = path.absolute().parent.parent

        path /= name

        if path.exists():
            return path

        path = path.parent.parent / name

        if path.exists():
            return path

        raise FileNotFoundError(f'No "{name}" directory found at "{path}"')

    def write_json(self, obj) -> int:
        """

        Write the specified object to the path as a JSON string

        """
        from fmtr.tools import json
        json_str = json.to_json(obj)
        return self.write_text(json_str, encoding=ToolsConfig.ENCODING)

    def read_json(self) -> Any:
        """

        Read JSON from the file and return as a Python object

        """
        from fmtr.tools import json
        json_str = self.read_text(encoding=ToolsConfig.ENCODING)
        obj = json.from_json(json_str)
        return obj

    def write_yaml(self, obj) -> int:
        """

        Write the specified object to the path as a JSON string

        """
        from fmtr.tools import yaml
        yaml_str = yaml.to_yaml(obj)
        return self.write_text(yaml_str, encoding=ToolsConfig.ENCODING)

    def read_yaml(self) -> Any:
        """

        Read YAML from the file and return as a Python object

        """
        from fmtr.tools import yaml
        yaml_str = self.read_text(encoding=ToolsConfig.ENCODING)
        obj = yaml.from_yaml(yaml_str)
        return obj

    def mkdirf(self):
        """

        Convenience method for creating directory with parents

        """
        return self.mkdir(parents=True, exist_ok=True)


