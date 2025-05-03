from typing import Any
import warnings

warnings.filterwarnings("ignore")

TyDic = dict[Any, Any]
TyDoD = dict[Any, TyDic]
TyDoEq = dict[str, str | dict[str, str]]


class Parms:
    """
    Define valid Parameters with default values
    """
    d_eq: TyDoEq = {
        'setup': {
            'cmd': 'str',

            'package': 'str',

            'app_home': 'str',
            'app_data': 'str',
            'tenant': 'str',

            'aodod_copy': 'list',

            'log_sw_mkdirs': 'bool',
            'log_sw_single_dir': 'bool',
            'log_type': 'str',
            'log_ts_type': 'str',
            'sw_debug': 'bool',
        },
        'mailsnd': {
            'cmd': 'str',
            'package': 'str',

            'app_home': 'str',
            'app_data': 'str',
            'tenant': 'str',

            'in_path_aod_snd': 'str',

            'log_sw_mkdirs': 'bool',
            'log_sw_single_dir': 'bool',
            'log_type': 'str',
            'log_ts_type': 'str',
            'sw_debug': 'bool',
        },
        'mailrcv': {
            'cmd': 'str',
            'package': 'str',

            'app_home': 'str',
            'app_data': 'str',
            'tenant': 'str',

            'in_path_aod_rcv': 'str',

            'log_sw_mkdirs': 'bool',
            'log_sw_single_dir': 'bool',
            'log_type': 'str',
            'log_ts_type': 'str',
            'sw_debug': 'bool',
        },
    }
