# coding=utf-8
from typing import Any

import os

from ka_uts_uts.utils.pac import Pac

TyArr = list[Any]
TyDic = dict[Any, Any]
TyPath = str
TyStr = str
TyTup = tuple[Any, Any]


class PacMod:
    """ Package Module Management
    """
    @staticmethod
    def sh_t_pacmod(cls) -> TyTup:
        """ Show Pacmod Dictionary
        """
        a_pacmod: TyArr = cls.__module__.split(".")
        return (a_pacmod[0], a_pacmod[1])

    @staticmethod
    def sh_d_pacmod(cls) -> TyDic:
        """ Show Pacmod Dictionary
        """
        a_pacmod: TyArr = cls.__module__.split(".")
        return {'package': a_pacmod[0], 'module': a_pacmod[1]}

    @staticmethod
    def sh_path_module_yaml(d_pacmod: TyDic) -> Any:
        """ show directory
        """
        package = d_pacmod['package']
        module = d_pacmod['module']
        path = f"{module}/data/{module}.yml"
        return Pac.sh_path_by_package(package, path)

    @classmethod
    def sh_path_keys_yml(cls, cls_com) -> Any:
        """
        show path to configuration yaml-file in data directory of package
        """
        _d_pacmod = cls.sh_d_pacmod(cls_com)
        _package = _d_pacmod['package']
        _path = os.path.join('data', 'keys.yml')
        return Pac.sh_path_by_package(_package, _path)

    @classmethod
    def sh_path_cfg_yml(cls, cls_app) -> Any:
        """
        show path to configuration yaml-file in data directory of package
        """
        _d_pacmod = cls.sh_d_pacmod(cls_app)
        _package = _d_pacmod['package']
        _path = os.path.join('data', 'cfg.yml')
        return Pac.sh_path_by_package(_package, _path)

    @classmethod
    def sh_dir_type(cls, kwargs: TyDic, type_: TyStr) -> TyPath:
        """
        Show run_dir
        """
        app_com = kwargs.get('app_com')
        app_data = kwargs.get('app_data', '')
        tenant = kwargs.get('tenant', '')
        package, module = cls.sh_t_pacmod(app_com)
        # dir_dat: str = com.dir_dat
        # tenant: str = com.tenant
        # package: str = com.d_app_pacmod['package']
        # module: str = com.d_app_pacmod['module']
        return os.path.join(app_data, tenant, package, module, type_)

    @classmethod
    def sh_path_pattern(
            cls, kwargs: TyDic, filename, type_: str, suffix: str) -> TyPath:
        """
        show type specific path
        """
        _dir: str = cls.sh_dir_type(kwargs, type_)
        return os.path.join(_dir, f"{filename}*.{suffix}")
