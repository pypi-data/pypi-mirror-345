# coding=utf-8
from typing import Any

import os
import importlib.resources as resources

# from ka_uts_log.log import LogEq

TyArr = list[Any]
TyDic = dict[Any, Any]
TyPackage = str
TyPackages = list[str]
TyPath = str
TnPath = None | TyPath


class Pac:

    @staticmethod
    def sh_path_in_cls(cls, path: TyPath) -> Any:
        """ show directory
        """
        _d_pacmod = cls.d_pacmod(cls)
        _package = _d_pacmod['package']
        return cls.sh_path_by_package(_package, path)

    @staticmethod
    def _sh_path_by_package(package: TyPackage, path: TyPath) -> Any:
        """ show directory
        """
        # _dirname = os.path.dirname(path)
        # _basename = os.path.basename(path)
        _path = str(resources.files(package).joinpath(path))
        # print(f"_sh_path_by_package package = {package}")
        # print(f"_sh_path_by_package path = {path}")
        # print(f"_sh_path_by_package _path = {_path}")
        if not _path:
            return ''
        # if _basename:
        #    _path = os.path.join(_path, _basename)
        if os.path.exists(_path):
            return _path
        # else:
        #    msg = f"_path = {_path} does not exist"
        #    raise Exception(msg)
        return ''

    @classmethod
    def sh_path_by_package(
            cls, package: TyPackage, path: TyPath, path_prefix: TnPath = None
    ) -> Any:
        """ show directory
        """
        if path_prefix:
            _path = os.path.join(path_prefix, path)
            # _dirname = os.path.dirname(_path)
            if os.path.exists(_path):
                return _path
        return cls._sh_path_by_package(package, path)

    @classmethod
    def sh_path_by_packages(
            cls, packages: TyPackages, path: TyPath, path_prefix: TnPath = None
    ) -> Any:
        """ show directory
        """
        if path_prefix:
            _path = os.path.join(path_prefix, path)
            # _dirname = os.path.dirname(_path)
            if os.path.exists(_path):
                return _path

        if not isinstance(packages, list):
            packages = [packages]

        for _package in packages:
            _path = cls._sh_path_by_package(_package, path)
            if _path:
                return _path
        return ''
