# -*- coding:utf-8 -*-
"""
管理员处理接口， 通过id查询信息，通过id删除， 增加管理员记录
"""

from flask.blueprints import Blueprint
from flask import jsonify, abort, current_app, request

from .utils import PermissionView
from .sta_code import SUCCESS, USER_SAME_LOGIN_NAME, OTHER_ERROR, POST_PARA_ERROR, QUERY_NO_RESULT, USER_DELETE_ERROR
from .sta_code import DELETE_NOT_EXITS
from ..service.user_admin_service import SmUserAdminService

user_admin_bp = Blueprint('user/admin', __name__)


class CreateAdmin(PermissionView):
    """
    创建管理员
    """
    para_legal_list_recv = ['LoginName', 'NickName', 'Password']

    def response_admin(self):
        try:
            result = SmUserAdminService.create_admin(CreatorID=self.u_id, **self.unpack_para(request.json))
            if result == 0:
                return jsonify(SUCCESS())
            elif result == 1:
                return jsonify(USER_SAME_LOGIN_NAME)
            elif result == 2:
                return jsonify(OTHER_ERROR)
        except Exception as e:    # 参数解析错误
            current_app.logger.error(e)
            return jsonify(POST_PARA_ERROR)
        return jsonify(OTHER_ERROR)


class QueryAllAdmin(PermissionView):
    """
    查询所有的管理员
    """
    para_legal_list_recv = ['Page', 'PageSize']
    para_legal_list_return = ['Password', 'CreatorID', 'RoleID', 'Lock']

    def response_admin(self):
        try:
            code, data = SmUserAdminService.query_admin(**self.unpack_para(request.json))
            if code == 0:
                self.pop_no_need(data['rows'])
                return jsonify(SUCCESS(data))
            elif code == 1:
                return jsonify(OTHER_ERROR)
        except Exception as e:    # 参数解析错误
            current_app.logger.error(e)
            return jsonify(POST_PARA_ERROR)
        return jsonify(OTHER_ERROR)


class QueryAdminByID(PermissionView):
    """
    通过id查询管理员详细信息
    """

    para_legal_list_return = ['Password', 'CreatorID', 'Forbidden', 'RoleID', 'Lock']

    def __init__(self):
        super(QueryAdminByID, self).__init__()
        self.admin_id = None    # 带查询的管理员id

    def dispatch_request(self, token_dict: dict, admin_id):
        self.admin_id = admin_id
        return super(QueryAdminByID, self).dispatch_request(token_dict)

    def response_admin(self):
        result = SmUserAdminService.get_by_id(self.admin_id)
        if result:
            self.pop_no_need(result)
            return jsonify(SUCCESS(result))
        else:
            return jsonify(QUERY_NO_RESULT)


class ChangeAdminByID(PermissionView):
    """
    通过id修改管理员信息
    """
    para_legal_list_recv = ['LoginName', 'NickName']

    def __init__(self):
        super(ChangeAdminByID, self).__init__()
        self.admin_id = None    # 带查询的管理员id

    def dispatch_request(self, token_dict: dict, admin_id):
        self.admin_id = admin_id
        return super(ChangeAdminByID, self).dispatch_request(token_dict)

    def response_admin(self):
        try:
            result = SmUserAdminService.update_by_id(self.admin_id, **self.unpack_para(request.json))
            if result == 0:
                return jsonify(SUCCESS())
            elif result == 1:
                return jsonify(DELETE_NOT_EXITS)
            elif result == 2:
                return jsonify(USER_SAME_LOGIN_NAME)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(POST_PARA_ERROR)


class DeleteAdminByID(PermissionView):
    """
    通过id删除管理员
    """

    def __init__(self):
        super(DeleteAdminByID, self).__init__()
        self.admin_id = None    # 带查询的管理员id

    def dispatch_request(self, token_dict: dict, admin_id):
        self.admin_id = admin_id
        return super(DeleteAdminByID, self).dispatch_request(token_dict)

    def response_admin(self):
        result = SmUserAdminService.delete_by_id(self.admin_id)
        if result == 0:
            return jsonify(SUCCESS())
        elif result == 1:
            return jsonify(DELETE_NOT_EXITS)
        elif result == 2:
            return jsonify(USER_DELETE_ERROR)
        return jsonify(OTHER_ERROR)


# 创建管理员
user_admin_bp.add_url_rule('/create', methods=['POST'], view_func=CreateAdmin.as_view('create_admin'))
# 查询所有管理员
user_admin_bp.add_url_rule('/all', methods=['POST'], view_func=QueryAllAdmin.as_view('all_admin'))
# 查询单个管理员，通过id
user_admin_bp.add_url_rule('/query/<admin_id>', methods=['POST'], view_func=QueryAdminByID.as_view('query_admin_by_id'))
# 通过id修改管理员
user_admin_bp.add_url_rule('/update/<admin_id>', methods=['POST'], view_func=ChangeAdminByID.as_view('update_admin_by_id'))
# 通过id删除管理员
user_admin_bp.add_url_rule('/delete/<admin_id>', methods=['POST'], view_func=DeleteAdminByID.as_view('delete_admin_by_id'))

