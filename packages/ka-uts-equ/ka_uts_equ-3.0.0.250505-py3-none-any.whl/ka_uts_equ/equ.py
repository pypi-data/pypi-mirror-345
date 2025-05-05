# coding=utf-8
from typing import Any
from collections.abc import Callable

from ka_uts_obj.str import Str
from ka_uts_obj.date import Date


TyArr = list[Any]
TyCall = Callable[..., Any]
TyDic = dict[Any, Any]
TyStr = str

TnArr = None | TyArr
TnDic = None | TyDic
TnStr = None | str


class AoEqu:
    """ Dictionary of Equates
    """
    @staticmethod
    def init_d_eq(a_equ: TyArr) -> TyDic:
        d_eq = {}
        for s_eq in a_equ[1:]:
            a_eq = s_eq.split('=')
            if len(a_eq) == 1:
                d_eq['cmd'] = a_eq[0]
            else:
                d_eq[a_eq[0]] = a_eq[1]
                d_eq[a_eq[0]] = a_eq[1]
        return d_eq

    @classmethod
    def sh_d_eq(cls, a_equ: TyArr, **kwargs) -> TyDic:
        """ show equates dictionary
        """
        d_parms: TnDic = kwargs.get('d_parms')
        _sh_prof = kwargs.get('sh_prof')
        d_eq: TyDic = cls.init_d_eq(a_equ)
        d_eq_new: TyDic = DoEqu.verify(d_eq, d_parms)
        DoEqu._set_sh_prof(d_eq_new, _sh_prof)
        return d_eq_new


class DoEqu:
    """ Manage Commandline Arguments
    """
    @classmethod
    def sh_value(cls, key: str, value: Any, d_valid_parms: TnDic) -> Any:

        # Log.debug("key", key)
        # Log.debug("value", value)
        if not d_valid_parms:
            return value
        _type: TnStr = d_valid_parms.get(key)
        if not _type:
            return value
        if isinstance(_type, str):
            match _type:
                case 'int':
                    value = int(value)
                case 'bool':
                    value = Str.sh_boolean(value)
                case 'dict':
                    print(f"DoEqu dict value = {value}")
                    value = Str.sh_dic(value)
                    print(f"DoEqu dict value = {value}")
                case 'list':
                    value = Str.sh_arr(value)
                case '%Y-%m-%d':
                    value = Date.sh(value, _type)
                case '_':
                    match _type[0]:
                        case '[', '{':
                            _obj = Str.sh_dic(_type)
                            if value not in _obj:
                                msg = (f"parameter={key} value={value} is invalid; "
                                       f"valid values are={_obj}")
                                raise Exception(msg)

        # Log.debug("value", value)
        return value

    @staticmethod
    def _set_sh_prof(d_eq: TyDic, sh_prof: TyCall | Any) -> None:
        """ set current pacmod dictionary
        """
        if callable(sh_prof):
            d_eq['sh_prof'] = sh_prof()
        else:
            d_eq['sh_prof'] = sh_prof

    @classmethod
    def verify(cls, d_eq: TyDic, d_parms: TnDic) -> TyDic:
        if d_parms is None:
            return d_eq
        if 'cmd' in d_eq:
            _d_valid_parms = d_parms
            _cmd = d_eq['cmd']
            _valid_commands = list(d_parms.keys())
            if _cmd not in _valid_commands:
                msg = (f"Wrong command: {_cmd}; "
                       f"valid commands are: {_valid_commands}")
                raise Exception(msg)
            _d_valid_parms = d_parms[_cmd]
        else:
            _d_valid_parms = d_parms
        if _d_valid_parms is None:
            return d_eq

        d_eq_new = {}
        for key, value in d_eq.items():
            if key not in _d_valid_parms:
                msg = (f"Wrong parameter: {key}; "
                       f"valid parameters are: {_d_valid_parms}")
                raise Exception(msg)
            d_eq_new[key] = cls.sh_value(key, value, _d_valid_parms)
        return d_eq_new
