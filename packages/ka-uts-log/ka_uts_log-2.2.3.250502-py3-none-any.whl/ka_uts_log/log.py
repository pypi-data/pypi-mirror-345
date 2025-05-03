from typing import Any
from collections.abc import Callable

import os
import time
import calendar
from datetime import datetime
import logging
import logging.config
from logging import Logger
import psutil

from ka_uts_uts.ioc.jinja2_ import Jinja2_
from ka_uts_uts.utils.pac import Pac
from ka_uts_uts.utils.pacmod import PacMod
from ka_uts_arr.aopath import AoPath

TyAny = Any
TyCallable = Callable[..., Any]
TyDateTime = datetime
TyTimeStamp = int
TyArr = list[Any]
TyBool = bool
TyDic = dict[Any, Any]
TyDir = str
TyPath = str
TyLogger = Logger
TyStr = str

TnAny = None | Any
TnArr = None | TyArr
TnBool = None | bool
TnDic = None | TyDic
TnTimeStamp = None | TyTimeStamp
TnDateTime = None | TyDateTime
TnStr = None | TyStr


class LogEq:
    """Logging Class
    """
    @staticmethod
    def sh(key: Any, value: Any) -> TyStr:
        return f"{key} = {value}"

    @classmethod
    def debug(cls, key: Any, value: Any) -> None:
        Log.debug(cls.sh(key, value), stacklevel=3)

    @classmethod
    def info(cls, key: Any, value: Any) -> None:
        Log.info(cls.sh(key, value), stacklevel=3)

    @classmethod
    def warning(cls, key: Any, value: Any) -> None:
        Log.warning(cls.sh(key, value), stacklevel=3)

    @classmethod
    def error(cls, key: Any, value: Any) -> None:
        Log.error(cls.sh(key, value), stacklevel=3)

    @classmethod
    def critical(cls, key: Any, value: Any) -> None:
        Log.critical(cls.sh(key, value), stacklevel=3)


class LogDic:

    @classmethod
    def debug(cls, dic: TyDic) -> None:
        for key, value in dic.items():
            LogEq.debug(key, value)

    @classmethod
    def info(cls, dic: TyDic) -> None:
        for key, value in dic.items():
            LogEq.info(key, value)

    @classmethod
    def warning(cls, dic: TyDic) -> None:
        for key, value in dic.items():
            LogEq.warning(key, value)

    @classmethod
    def error(cls, dic: TyDic) -> None:
        for key, value in dic.items():
            LogEq.error(key, value)

    @classmethod
    def critical(cls, dic: TyDic) -> None:
        for key, value in dic.items():
            LogEq.critical(key, value)


class Log:

    sw_init: bool = False
    log: TyLogger = logging.getLogger('dummy_logger')
    # log_type: TyStr = 'std'
    # pid = os.getpid()
    # ts = calendar.timegm(time.gmtime())
    # username: TyStr = psutil.Process().username()
    # path_log_cfg: TyStr = ''
    # d_pacmod: TyDic = {}
    # d_app_pacmod: TyDic = {}

    @classmethod
    def debug(cls, *args, **kwargs) -> None:
        if kwargs is None:
            kwargs = {}
        kwargs['stacklevel'] = kwargs.get('stacklevel', 2)
        cls.log.debug(*args, **kwargs)

    @classmethod
    def info(cls, *args, **kwargs) -> None:
        if kwargs is None:
            kwargs = {}
        kwargs['stacklevel'] = kwargs.get('stacklevel', 2)
        cls.log.info(*args, **kwargs)

    @classmethod
    def warning(cls, *args, **kwargs) -> None:
        if kwargs is None:
            kwargs = {}
        kwargs['stacklevel'] = kwargs.get('stacklevel', 2)
        cls.log.warning(*args, **kwargs)

    @classmethod
    def error(cls, *args, **kwargs) -> None:
        if kwargs is None:
            kwargs = {}
        kwargs['stacklevel'] = kwargs.get('stacklevel', 2)
        cls.log.error(*args, **kwargs)

    @classmethod
    def critical(cls, *args, **kwargs) -> None:
        if kwargs is None:
            kwargs = {}
        kwargs['stacklevel'] = kwargs.get('stacklevel', 2)
        cls.log.critical(*args, **kwargs)

    @classmethod
    def sh_dir_run(cls, kwargs) -> TyDir:
        """Show run_dir
        """
        _app_data: str = kwargs.get('app_data', '/data')
        _tenant: str = kwargs.get('tenant', '')
        _cls_app = kwargs.get('cls_app')
        _d_app_pacmod = PacMod.sh_d_pacmod(_cls_app)
        _package = _d_app_pacmod['package']
        _path = os.path.join(_app_data, _tenant, 'RUN', _package)
        _cmd: TnStr = kwargs.get('cmd')
        _log_type = kwargs.get('log_type', 'std')
        if _log_type == "usr":
            _username: TyStr = psutil.Process().username()
            _path = os.path.join(_path, _username)
        if _cmd is not None:
            _path = os.path.join(_path, _cmd)
        return _path

    @classmethod
    def sh_d_dir_run(cls, kwargs) -> TyDic:
        """Read log file path with jinja2
        """
        _dir_run = cls.sh_dir_run(kwargs)
        if kwargs.get('sw_single_log_dir', True):
            return {
                    'dir_run_debs': f"{_dir_run}/debs",
                    'dir_run_infs': f"{_dir_run}/logs",
            }
        return {
                'dir_run_debs': f"{_dir_run}/debs",
                'dir_run_infs': f"{_dir_run}/infs",
                'dir_run_wrns': f"{_dir_run}/wrns",
                'dir_run_errs': f"{_dir_run}/errs",
                'dir_run_crts': f"{_dir_run}/crts",
        }

    @classmethod
    def sh_path_log_cfg(cls_log, kwargs: TyDic) -> Any:
        """ show directory
        """
        _log_type = kwargs.get('log_type', 'std')
        _cls_app = kwargs.get('cls_app')
        _d_log_pacmod = PacMod.sh_d_pacmod(cls_log)
        _d_app_pacmod = PacMod.sh_d_pacmod(_cls_app)
        _app_package = _d_app_pacmod['package']
        _log_package = _d_log_pacmod['package']
        _packages = [_app_package, _log_package]
        _path = os.path.join('cfg', f"log.{_log_type}.yml")
        _path = Pac.sh_path_by_packages(_packages, _path)
        return _path

    @staticmethod
    def sh_calendar_ts(kwargs) -> Any:
        """Set static variable log level in log configuration handlers
        """
        _log_ts_type = kwargs.get('log_ts_type', 'ts')
        if _log_ts_type == 'ts':
            return calendar.timegm(time.gmtime())
        else:
            return calendar.timegm(time.gmtime())

    @classmethod
    def sh_d_log_cfg(cls, kwargs: TyDic) -> TyDic:
        """Read log file path with jinja2
        """
        _d_dir_run = cls.sh_d_dir_run(kwargs)
        if kwargs.get('log_sw_mkdirs', True):
            AoPath.mkdirs(list(_d_dir_run.values()), exist_ok=True)

        _cls_app = kwargs.get('cls_app')
        _d_app_pacmod = PacMod.sh_d_pacmod(_cls_app)

        _path_log_cfg = cls.sh_path_log_cfg(kwargs)
        _ts = cls.sh_calendar_ts(kwargs)
        _pid = os.getpid()
        _module = _d_app_pacmod['module']
        _d_log_cfg: TyDic = Jinja2_.read(
                _path_log_cfg, cls.log,
                module=_module, pid=_pid, ts=_ts, **_d_dir_run)
        sw_debug: TyBool = kwargs.get('sw_debug', False)
        if sw_debug:
            level = logging.DEBUG
        else:
            level = logging.INFO
        _log_type = kwargs.get('log_type', 'std')
        logger_name = _log_type
        _d_log_cfg['handlers'][f"{logger_name}_debug_console"]['level'] = level
        _d_log_cfg['handlers'][f"{logger_name}_debug_file"]['level'] = level
        return _d_log_cfg

    @classmethod
    def init(cls, **kwargs) -> None:
        """Set static variable log level in log configuration handlers
        """
        if cls.sw_init:
            return
        # cls.log_type = kwargs.get('log_type', 'std')
        # cls.ts = cls.sh_calendar_ts(kwargs))

        # cls.d_pacmod = PacMod.sh_d_pacmod(cls)
        # cls_app = kwargs.get('cls_app')
        # cls.d_app_pacmod = PacMod.sh_d_pacmod(cls_app)

        _d_log_cfg = cls.sh_d_log_cfg(kwargs)
        _log_type = kwargs.get('log_type', 'std')
        logging.config.dictConfig(_d_log_cfg)
        cls.log = logging.getLogger(_log_type)
        cls.sw_init = True

    @classmethod
    def sh(cls, **kwargs) -> Any:
        if cls.sw_init:
            return cls
            # return cls.log
        cls.init(**kwargs)
        return cls
