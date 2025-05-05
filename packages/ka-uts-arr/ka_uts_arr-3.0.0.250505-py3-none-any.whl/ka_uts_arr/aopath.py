# coding=utf-8
from collections.abc import Callable, Iterator
from typing import Any

import glob
import os

TyArr = list[Any]
TyCallable = Callable[..., Any]
TyPath = str
TyAoPath = list[TyPath]
TyDic = dict[Any, Any]
TyIterAny = Iterator[Any]
TyIterPath = Iterator[TyPath]
TyTup = tuple[Any, ...]
TyIterTup = Iterator[TyTup]

TnArr = None | TyArr
TnDic = None | TyDic


class AoPath:

    # @staticmethod
    # def join(a_path: TyAoPath) -> TyPath:
    #     _sep = os.sep
    #     _a_path: TyAoPath = []
    #     for _path in a_path:
    #         _path = _path.lstrip(_sep)
    #         _path = _path.rstrip(_sep)
    #         _path = _sep + _path.rstrip(_sep)
    #         _a_path.append(_path)
    #     path_new: TyPath = ''.join(_a_path)
    #     return path_new

    @staticmethod
    def join(aopath: TyAoPath) -> TyPath:
        _sep = os.sep
        return ''.join([_sep+_path.strip(_sep) for _path in aopath if _path])

    @staticmethod
    def mkdirs(aopath: TyAoPath, **kwargs) -> None:
        if not aopath:
            return
        for _path in aopath:
            os.makedirs(_path, **kwargs)

    @staticmethod
    def sh_a_path(
            path: TyPath) -> TyAoPath:
        a_path: TyAoPath = glob.glob(path)
        return a_path

    @classmethod
    def sh_a_path_by_tmpl(
            cls, a_path_tmpl_key: TyAoPath, kwargs: TyDic) -> TyAoPath:
        _a_path_tmpl: TyAoPath = cls.sh_items_in_dic(a_path_tmpl_key, kwargs)
        _path_tmpl: TyPath = cls.join(_a_path_tmpl)
        return cls.sh_a_path(_path_tmpl)

    @staticmethod
    def sh_items_in_dic(arr: TnArr, dic: TnDic) -> TyArr:
        # def sh_values(arr: TnArr, dic: TnDic) -> TyArr:
        arr_new: TyArr = []
        if not arr:
            return arr_new
        if not dic:
            return arr_new
        for _key in arr:
            if _key in dic:
                arr_new.append(dic[_key])
        return arr_new

    @classmethod
    def yield_path_kwargs_over_path(
        # def yield_over_a_path(
            cls, a_path_tmpl_key: TyAoPath, kwargs: TyDic
    ) -> TyIterTup:
        _a_path: TyAoPath = cls.sh_a_path_by_tmpl(a_path_tmpl_key, kwargs)
        for _path in _a_path:
            yield (_path, kwargs)

    @classmethod
    def yield_path_kwargs_over_dir_path(
        # def yield_path_kwargs_new(
        # def yield_over_a_dir_a_path(
            cls,
            a_dir_tmpl_key: TyAoPath,
            a_path_tmpl_key: TyAoPath,
            sh_kwargs_new: TyCallable,
            kwargs: TyDic
    ) -> TyIterTup:
        _a_dir: TyAoPath = cls.sh_a_path_by_tmpl(a_dir_tmpl_key, kwargs)
        for _dir in _a_dir:
            _kwargs_new: TyDic = sh_kwargs_new([_dir, kwargs])
            _a_path: TyAoPath = cls.sh_a_path_by_tmpl(
                    a_path_tmpl_key, _kwargs_new)
            for _path in _a_path:
                yield (_path, _kwargs_new)

    @classmethod
    def yield_path_item_kwargs_over_path_arr(
        # def yield_path_item_kwargs(
        # def yield_over_a_path_arr(
            cls, a_path_tmpl_key: TyAoPath, arr_key: str, kwargs: TyDic
    ) -> TyIterTup:
        _a_path: TyAoPath = cls.sh_a_path_by_tmpl(a_path_tmpl_key, kwargs)
        _arr: TyAoPath = kwargs.get(arr_key, [])
        for _path in _a_path:
            for _item in _arr:
                yield (_path, _item, kwargs)

    @classmethod
    def yield_path_item_kwargs_over_dir_path_arr(
        # def yield_path_item_kwargs_new(
        # def yield_over_a_dir_a_path_arr(
            cls,
            a_dir_tmpl_key: TyAoPath,
            a_path_tmpl_key: TyAoPath,
            arr_key: str,
            sh_kwargs_new: TyCallable,
            kwargs: TyDic
    ) -> TyIterTup:
        _a_dir: TyAoPath = cls.sh_a_path_by_tmpl(a_dir_tmpl_key, kwargs)
        _arr: TyAoPath = kwargs.get(arr_key, [])
        for _dir in _a_dir:
            _kwargs_new: TyDic = sh_kwargs_new([_dir, kwargs])
            _a_path: TyAoPath = cls.sh_a_path_by_tmpl(
                    a_path_tmpl_key, _kwargs_new)
            for _path in _a_path:
                for _item in _arr:
                    yield (_path, _item, _kwargs_new)
