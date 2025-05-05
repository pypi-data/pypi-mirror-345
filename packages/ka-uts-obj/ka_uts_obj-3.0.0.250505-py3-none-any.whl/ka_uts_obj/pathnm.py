from typing import Any

import os

from ka_uts_log.log import LogEq
from ka_uts_obj.path import Path

TyDic = dict[Any, Any]
TyPath = str

TnDic = None | TyDic
TnPath = None | TyPath


class PathNm:

    @classmethod
    def sh_path(cls, pathnm: str, kwargs: TyDic) -> TyPath:
        # def sh_path_by_pathnm(cls, pathnm: str, **kwargs) -> str:
        _path: TyPath = kwargs.get(pathnm, '')
        _path_prefixes = kwargs.get('path_prefixes', [])
        LogEq.debug("pathnm", pathnm)
        LogEq.debug("_path_prefixes", _path_prefixes)
        _paths = []
        for _path_prefix in _path_prefixes:
            _value = kwargs.get(_path_prefix)
            if _value:
                _paths.append(_value)
        _paths.append(_path)
        LogEq.debug("_paths", _paths)
        _path = os.path.join(*_paths)
        _path = Path.sh_path_using_d_path(_path, kwargs)
        _path = Path.sh_path_using_d_pathnm2datetype(_path, pathnm, kwargs)
        return _path
