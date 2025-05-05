# coding=utf-8
from collections.abc import Iterator
from typing import Any

import os
import datetime
import glob
import pathlib
from string import Template
import re

from ka_uts_log.log import LogEq

TyArr = list[Any]
TyAoS = list[str]
TyAoA = list[TyArr]
TyDic = dict[Any, Any]
TyDoA = dict[Any, TyArr]
TyDoAoA = dict[Any, TyAoA]
TyDoInt = dict[str, int]
TyDoDoInt = dict[str, TyDoInt]
TyIntStr = int | str
TyPath = str
TyBasename = str
TyIterAny = Iterator[Any]
TyStr = str
TyTup = tuple[Any]

TnArr = None | TyArr
TnAoA = None | TyAoA
TnDic = None | TyDic
TnInt = None | int
TnPath = None | TyPath
TnStr = None | str
TnTup = None | TyTup


class Path:

    @staticmethod
    def verify(path: TyPath) -> None:
        if path is None:
            raise Exception("path is None")
        elif path == '':
            raise Exception("path is empty")

    @classmethod
    def edit_path(cls, path: TyPath, kwargs: TyDic) -> TyPath:
        _d_edit = kwargs.get('d_out_path_edit', {})
        _prefix = kwargs.get('dl_out_file_prefix', '')
        _suffix = kwargs.get('dl_out_file_suffix', '.csv')
        _edit_from = _d_edit.get('from')
        _edit_to = _d_edit.get('to')
        if _edit_from is not None and _edit_to is not None:
            _path_out = path.replace(_edit_from, _edit_to)
        else:
            _path_out = path
        _dir_out = os.path.dirname(_path_out)
        cls.mkdir_from_path(_dir_out)
        _basename_out = os.path.basename(_path_out)
        if _prefix:
            _basename_out = str(f"{_prefix}{_basename_out}")
        if _suffix:
            _basename_out = os.path.splitext(_basename_out)[0]
            _basename_out = str(f"{_basename_out}{_suffix}")
        _path_out = os.path.join(_dir_out, _basename_out)
        return _path_out

    @staticmethod
    def mkdir(path: TyPath) -> None:
        if not os.path.exists(path):
            # Create the directory
            os.makedirs(path)

    @staticmethod
    def mkdir_from_path(path: TyPath) -> None:
        _dir = os.path.dirname(path)
        if not os.path.exists(_dir):
            # Create the directory
            os.makedirs(_dir)

    @staticmethod
    def sh_basename(path: TyPath) -> TyBasename:
        """ Extracts basename of a given path.
            Should Work with any OS Path on any OS
        """
        raw_string = r'[^\\/]+(?=[\\/]?$)'
        basename = re.search(raw_string, path)
        if basename:
            return basename.group(0)
        return path

    @classmethod
    def sh_components(
        # def sh_component(
            cls, path: TyPath, d_ix: TyDic, separator: str = "-") -> TnStr:
        ix_start = d_ix.get("start")
        ix_add = d_ix.get("add", 0)
        if not ix_start:
            return None
        _a_dir: TyArr = cls.split_to_array(path)
        _ix_end = ix_start + ix_add + 1
        _component = separator.join(_a_dir[ix_start:_ix_end])
        _a_component = os.path.splitext(_component)
        return _a_component[0]

    @classmethod
    def sh_component_using_field_name(
        # def sh_component_at_start(
            cls, path: TyPath, d_path_ix: TyDoDoInt, field_name: str) -> TyStr:
        _d_ix: TyDoInt = d_path_ix.get(field_name, {})
        if not _d_ix:
            msg = f"field_name: {field_name} is not defined in dictionary: {d_path_ix}"
            raise Exception(msg)
        _start = _d_ix.get('start')
        if not _start:
            msg = f"'start' is not defined in dictionary: {_d_ix}"
            raise Exception(msg)
        _a_dir: TyAoS = cls.split_to_array(path)
        if _start < len(_a_dir):
            return _a_dir[_start]
        msg = f"index: {_start} is out of range of list: {_a_dir}"
        raise Exception(msg)

    @staticmethod
    def sh_fnc_name_using_pathlib(path: TyPath) -> str:
        # def sh_fnc_name(path: TyPath) -> str:
        _purepath = pathlib.PurePath(path)
        dir_: str = _purepath.parent.name
        stem_: str = _purepath.stem
        return f"{dir_}-{stem_}"

    @staticmethod
    def sh_fnc_name_using_os_path(path: TyPath) -> str:
        # def sh_os_fnc_name(path: TyPath) -> str:
        split_ = os.path.split(path)
        dir_ = os.path.basename(split_[0])
        stem_ = os.path.splitext(split_[1])[0]
        return f"{dir_}-{stem_}"

    @classmethod
    def sh_last_component(cls, path: TyPath) -> Any:
        a_dir: TyArr = cls.split_to_array(path)
        return a_dir[-1]

    @staticmethod
    def sh_path_using_d_path(path: TyPath, kwargs: TyDic) -> TyPath:
        _d_path = kwargs.get('d_path', {})
        if not _d_path:
            return path
        return Template(path).safe_substitute(_d_path)

    @classmethod
    def sh_path_using_d_pathnm2datetype(
            cls, path: TyPath, pathnm: str, kwargs: TyDic) -> TyPath:
        LogEq.debug("pathnm", pathnm)
        _d_pathnm2datetype: TyDic = kwargs.get('d_pathnm2datetype', {})
        LogEq.debug("_d_pathnm2datetype", _d_pathnm2datetype)
        if not _d_pathnm2datetype:
            return path
        _datetype: TyStr = _d_pathnm2datetype.get(pathnm, '')
        _path = cls.sh_path_using_datetype(path, _datetype, kwargs)
        LogEq.debug("_path", _path)
        return _path

    @classmethod
    def sh_path_using_datetype(
            cls, path: TyPath, datetype: str, kwargs: TyDic) -> TyPath:
        LogEq.debug("path", path)
        LogEq.debug("datetype", datetype)
        match datetype:
            case 'last':
                path_new = cls.sh_path_last(path)
            case 'first':
                path_new = cls.sh_path_first(path)
            case 'now':
                path_new = cls.sh_path_now(path, **kwargs)
            case _:
                path_new = cls.sh_path(path)
        LogEq.debug("path_new", path_new)
        return path_new

    @staticmethod
    def sh_path(path: TyPath) -> TyPath:
        LogEq.debug("path", path)
        if not path:
            raise Exception("Argument 'path' is empty")
        _a_path: TyArr = glob.glob(path)
        if not _a_path:
            msg = f"glob.glob find no paths for template: {path}"
            raise Exception(msg)
        path_new: str = sorted(_a_path)[0]
        return path_new

    @staticmethod
    def sh_path_first(path: TyPath) -> TyPath:
        if not path:
            raise Exception("Argument 'path' is empty")
        _a_path: TyArr = glob.glob(path)
        if not _a_path:
            msg = f"glob.glob find no paths for template: {path}"
            raise Exception(msg)
        path_new: str = sorted(_a_path)[0]
        return path_new

    @staticmethod
    def sh_path_last(path: TyPath) -> TyPath:
        if not path:
            raise Exception("Argument 'path' is empty")
        _a_path: TyArr = glob.glob(path)
        if not _a_path:
            msg = f"glob.glob find no paths for template: {path}"
            raise Exception(msg)
        path_new: str = sorted(_a_path)[-1]
        return path_new

    @staticmethod
    def sh_path_now(path: TyPath, **kwargs) -> TyPath:
        now_var = kwargs.get('now_var', 'now')
        now_fmt = kwargs.get('now_fmt', '%Y%m%d')
        if not path:
            raise Exception("Argument 'path' is empty")
        _current_date: str = datetime.datetime.now().strftime(now_fmt)
        _dic = {now_var: _current_date}
        path_new: str = Template(path).safe_substitute(_dic)
        return path_new

    @staticmethod
    def split_to_array(path: TyPath) -> TyArr:
        """ Convert path to normalized pyth
            Should Work with any OS Path on any OS
        """
        normalized_path = os.path.normpath(path)
        a_path: TyArr = normalized_path.split(os.sep)
        return a_path
