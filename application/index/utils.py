# -*- coding:utf-8 -*-
"""
定义一些基础东西
"""
import functools
from flask.views import View
from flask import abort, request, jsonify

from .sta_code import PERMISSION_DENIED_ERROR
from ..dao.utils import RedisOp
from ..service.auth import decode_auth_token
from ..service.utils import BaseService


def check_auth(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        auth = request.headers.get('auth', None)
        if auth is None:
            abort(404)
        token = RedisOp().get_normal(auth)
        # 检测不到token
        if token is None:
            abort(404)
        try:
            token_dict = decode_auth_token(token)
        except Exception as e:
            print(e)
            abort(404)
        return fn(token_dict, *args, **kwargs)
    return wrapper


class BaseView(View):
    """
    基础View，拦截未登录，进行预处理
    """
    para_legal_list_recv = []    # 接收参数过滤列表
    para_legal_list_return = []    # 返回参数过滤列表

    @classmethod
    def unpack_para(cls, params: dict):
        """
        解析出欲修改数据    para_legal_list_recv
        :param params: 所有参数
        :return:
        """
        return {key: params[key] for key in params.keys() if key in cls.para_legal_list_recv}

    @classmethod
    def pop_no_need(cls, a_para: dict):
        """
        弹出非必须参数    para_legal_list_return
        :param a_para: 弹出目标(list, 或者 dict)
        :return:
        """
        if isinstance(a_para, list):
            for para in a_para:
                for key in cls.para_legal_list_return:
                    para.pop(key, None)
        elif isinstance(a_para, dict):
            for key in cls.para_legal_list_return:
                a_para.pop(key, None)

    def dispatch_request(self):
        # 暂时404
        abort(404)


class PermissionView(BaseView):
    # 验证token
    decorators = (check_auth, )

    def __init__(self):
        self._token_data = None
        self.user = None
        self.u_id = None
        self.u_login_name = None
        self.u_nick_name = None
        self.u_role_id = None
        self.u_role_name = None

    def response_admin(self):
        abort(404)

    def response_agent(self):
        abort(404)

    def response_member(self):
        abort(404)

    def dispatch_request(self, token_dict: dict):
        self._token_data = token_dict['data']
        self.user = BaseService.is_forbidden(self._token_data['u_id'], self._token_data['u_role_name'])
        if self.user is None:
            return jsonify(PERMISSION_DENIED_ERROR)
        self.u_id = self._token_data['u_id']
        self.u_login_name = self._token_data['u_login_name']
        self.u_nick_name = self._token_data['u_nick_name']
        self.u_role_id = self._token_data['u_role_id']
        self.u_role_name = self._token_data['u_role_name']
        if self.u_role_name == 'Admin':
            return self.response_admin()
        elif self.u_role_name == 'Agent':
            return self.response_agent()
        elif self.u_role_name == 'Member':
            return self.response_member()

