# coding=utf-8
from typing import Any

import os
import importlib.resources as resources

# from ka_uts_log.log import LogEq
# from ka_uts_log.log import Log

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
        _path = str(resources.files(package).joinpath(path))
        if not _path:
            print(f"path {_path} is empty")
            return ''
        if os.path.exists(_path):
            print(f"path {_path} exists")
            return _path
        print(f"path {_path} does not exist")
        return ''

    @classmethod
    def sh_path_by_package(
            cls, package: TyPackage, path: TyPath, path_prefix: TnPath = None
    ) -> Any:
        """ show directory
        """
        print(f"path = {path}")
        print(f"path_prefix = {path_prefix}")
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
