import os

from ka_uts_log.log import LogEq
from ka_uts_uts.utils.pac import Pac
from ka_uts_obj.path import Path as Path

from typing import Any

TyPathLike = os.PathLike
TyAny = Any
TyArr = list[Any]
TyDic = dict[Any, Any]
TyPath = str
TyStr = str

TnAny = None | TyAny
TnDic = None | TyDic


class DoPath:

    @staticmethod
    def sh_path(dic: TyDic, kwargs: TyDic) -> TyPath:
        _paths: TyArr = []
        _path: TyPath = ''
        if not dic:
            return _path
        _package: TyStr = kwargs.get('package', '')
        LogEq.debug("dic", dic)
        _datetype = None
        for _k, _v in dic.items():
            LogEq.debug("_k", _k)
            LogEq.debug("_v", _v)
            if _k == 'datetype':
                _datetype = _v
            else:
                match _v:
                    case 'key':
                        _val = kwargs.get(_k)
                        if _val:
                            _paths.append(_val)
                    case 'pac':
                        _val = Pac.sh_path_by_package(_package, _k)
                        if _val:
                            _paths.append(_val)
                    case _:
                        _paths.append(_k)
        LogEq.debug("_paths", _paths)
        LogEq.debug("_datetype", _datetype)
        if _paths:
            _path = os.path.join(*_paths)
            LogEq.debug("_path", _path)
            if _datetype:
                _path = Path.sh_path_using_datetype(_path, _datetype, kwargs)
        return _path
