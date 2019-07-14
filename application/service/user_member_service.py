# -*- coding:utf-8 -*-
"""
会员相关service
"""
import datetime
from flask import current_app
from sqlalchemy import and_

from ..dao.models import db, SmUserAgent, SmUserMember, SmUser, SmUserRole, SmClerk, SmUserLog
from .utils import BaseService


class SmUserMemberService(BaseService):
    """
    代理业务逻辑代码
    """

    @classmethod
    def info_by_id(cls, uid):
        """
        获取会员信息
        :param uid: 目标id
        :return:
        """
        try:
            mid = SmUserMember.query.filter(
                and_(SmUserMember.ID == uid, SmUserMember.Forbidden == 0, SmUserMember.Lock < 6)).first()
            result = cls.model_to_dict_by_dict(mid)
            result['AgentName'] = mid.sm_user_agent.LoginName
            result['ClerkName'] = mid.sm_user_agent.NickName
            return result
        except Exception as e:
            current_app.logger.error(e)
            return None

    @classmethod
    def insert(cls, token_data, **para):
        date_time_now = datetime.datetime.now()     # 获取当前时间
        para['Password'] = cls.sha256_generator(para['Password'])     # 修正密码
        try:
            user = SmUser.query.filter(SmUser.LoginName == para['LoginName']).first()
            if user:     # 用户登录名已存在
                return 1
            member = None     # 待添加会员账号
            log = None     # 待添加日志
            role = SmUserRole.query.filter(SmUserRole.Name == 'Member').first()     # 获取role-----Member
            if token_data['u_role_name'] == 'Admin':     # 管理员创建
                agent = SmUserAgent.query.filter(SmUserAgent.ID == para['AgentID']).first()     # 获取待创建会员的代理
                if agent is None:     # 检测不到所需代理
                    return 1
                if para.get('ClerkID', None):     # 校验ClerkID 业务员ID
                    clerk = SmClerk.query.filter(SmClerk.ID == para['ClerkID'], SmClerk.AgentID == agent.ID).first()
                    para['ClerkID'] = None if clerk is None else clerk.ID
                # 生成所需会员对象
                member = SmUserMember(ID=cls.md5_generator('sm_user_member' + str(date_time_now)), Forbidden=0, Lock=0,
                                      CreatorID=token_data['u_id'], CreateTime=date_time_now, RoleID=role.ID, **para)
                log = SmUserLog(ID=cls.md5_generator('sm_user_log' + str(date_time_now)), UserID=token_data['u_id'],
                                Type=role.Description, Model='创建会员', Time=date_time_now,
                                Note='管理员 ' + token_data['u_login_name'] + '创建会员 ' + para['LoginName'])
            db.session.add(member)
            db.session.add(log)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            return 1
        return 0
